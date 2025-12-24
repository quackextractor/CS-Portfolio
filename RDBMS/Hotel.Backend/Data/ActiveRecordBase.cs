using System.Data;
using Microsoft.Data.SqlClient;
using System.Reflection;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Hotel.Backend.Data;

public abstract class ActiveRecordBase<T> where T : ActiveRecordBase<T>, new()
{
    // Assumes table name is plural of class name or specific attribute
    protected static string TableName
    {
        get
        {
            var attr = typeof(T).GetCustomAttribute<TableAttribute>();
            return attr?.Name ?? typeof(T).Name + "s";
        }
    }

    protected static string PrimaryKey => "Id"; // Simplification for assignment

    public int Id { get; set; }

    protected static SqlConnection GetConnection(SqlTransaction? transaction = null)
    {
        if (transaction != null)
        {
            return transaction.Connection;
        }
        return new SqlConnection(DbConfig.ConnectionString);
    }

    public static T? Find(int id, SqlTransaction? transaction = null)
    {
        var conn = GetConnection(transaction);
        if (transaction == null) conn.Open();
        
        try
        {
            var cmd = conn.CreateCommand();
            cmd.Transaction = transaction;
            cmd.CommandText = $"SELECT * FROM {TableName} WHERE {PrimaryKey} = @Id";
            cmd.Parameters.AddWithValue("@Id", id);

            using var reader = cmd.ExecuteReader();
            if (reader.Read())
            {
                return MapFromReader(reader);
            }
            return null;
        }
        finally
        {
            if (transaction == null) conn.Dispose();
        }
    }

    public static List<T> Where(string condition, Dictionary<string, object>? parameters = null, SqlTransaction? transaction = null)
    {
        var conn = GetConnection(transaction);
        if (transaction == null) conn.Open();
        
        try
        {
            var cmd = conn.CreateCommand();
            cmd.Transaction = transaction;
            cmd.CommandText = $"SELECT * FROM {TableName} WHERE {condition}";
            
            if (parameters != null)
            {
                foreach (var p in parameters)
                {
                    cmd.Parameters.AddWithValue(p.Key, p.Value ?? DBNull.Value);
                }
            }

            var list = new List<T>();
            using var reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                list.Add(MapFromReader(reader));
            }
            return list;
        }
        finally
        {
            if (transaction == null) conn.Dispose();
        }
    }

    public static List<T> All(SqlTransaction? transaction = null)
    {
        return Where("1=1", null, transaction);
    }


    public void Save(SqlTransaction? transaction = null)
    {
        if (Id == 0)
        {
            Insert(transaction);
        }
        else
        {
            Update(transaction);
        }
    }

    public void Delete(SqlTransaction? transaction = null)
    {
        var conn = GetConnection(transaction);
        if (transaction == null) conn.Open();
        
        try
        {
            var cmd = conn.CreateCommand();
            cmd.Transaction = transaction;
            cmd.CommandText = $"DELETE FROM {TableName} WHERE {PrimaryKey} = @Id";
            cmd.Parameters.AddWithValue("@Id", Id);
            cmd.ExecuteNonQuery();
        }
        finally
        {
            if (transaction == null) conn.Dispose();
        }
    }

    protected virtual void Insert(SqlTransaction? transaction = null)
    {
        var conn = GetConnection(transaction);
        if (transaction == null) conn.Open();

        try
        {
            var cmd = conn.CreateCommand();
            cmd.Transaction = transaction;

            var properties = GetMappedProperties();
            var columns = string.Join(", ", properties.Select(p => p.Name));
            var values = string.Join(", ", properties.Select(p => "@" + p.Name));

            cmd.CommandText = $"INSERT INTO {TableName} ({columns}) OUTPUT INSERTED.{PrimaryKey} VALUES ({values})";

            foreach (var p in properties)
            {
                cmd.Parameters.AddWithValue("@" + p.Name, p.GetValue(this) ?? DBNull.Value);
            }

            Id = (int)cmd.ExecuteScalar();
        }
        finally
        {
            if (transaction == null) conn.Dispose();
        }
    }

    protected virtual void Update(SqlTransaction? transaction = null)
    {
        var conn = GetConnection(transaction);
        if (transaction == null) conn.Open();

        try
        {
            var cmd = conn.CreateCommand();
            cmd.Transaction = transaction;

            var properties = GetMappedProperties();
            var sets = string.Join(", ", properties.Select(p => $"{p.Name} = @{p.Name}"));

            cmd.CommandText = $"UPDATE {TableName} SET {sets} WHERE {PrimaryKey} = @Id";

            cmd.Parameters.AddWithValue("@Id", Id);
            foreach (var p in properties)
            {
                cmd.Parameters.AddWithValue("@" + p.Name, p.GetValue(this) ?? DBNull.Value);
            }

            cmd.ExecuteNonQuery();
        }
        finally
        {
            if (transaction == null) conn.Dispose();
        }
    }

    private static T MapFromReader(SqlDataReader reader)
    {
        var entity = new T();
        var properties = typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Where(p => p.CanWrite && !Attribute.IsDefined(p, typeof(NotMappedAttribute)));

        foreach (var p in properties)
        {
            try
            {
                // Check if column exists
                for (int i = 0; i < reader.FieldCount; i++)
                {
                    if (reader.GetName(i).Equals(p.Name, StringComparison.OrdinalIgnoreCase))
                    {
                        var val = reader[i];
                        if (val != DBNull.Value)
                        {
                            p.SetValue(entity, val);
                        }
                        break;
                    }
                }
            }
            catch { /* Ignore mapping errors for now */ }
        }
        return entity;
    }

    private IEnumerable<PropertyInfo> GetMappedProperties()
    {
        return typeof(T).GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Where(p => p.Name != PrimaryKey && p.CanRead && !Attribute.IsDefined(p, typeof(NotMappedAttribute)));
    }
}
