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

    protected static SqlConnection GetConnection()
    {
        return new SqlConnection(DbConfig.ConnectionString);
    }

    public static T? Find(int id)
    {
        using var conn = GetConnection();
        conn.Open();
        var cmd = conn.CreateCommand();
        cmd.CommandText = $"SELECT * FROM {TableName} WHERE {PrimaryKey} = @Id";
        cmd.Parameters.AddWithValue("@Id", id);

        using var reader = cmd.ExecuteReader();
        if (reader.Read())
        {
            return MapFromReader(reader);
        }
        return null;
    }

    public static List<T> Where(string condition, Dictionary<string, object>? parameters = null)
    {
        using var conn = GetConnection();
        conn.Open();
        var cmd = conn.CreateCommand();
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

    public static List<T> All()
    {
        return Where("1=1");
    }

    public void Save()
    {
        if (Id == 0)
        {
            Insert();
        }
        else
        {
            Update();
        }
    }

    public void Delete()
    {
        using var conn = GetConnection();
        conn.Open();
        var cmd = conn.CreateCommand();
        cmd.CommandText = $"DELETE FROM {TableName} WHERE {PrimaryKey} = @Id";
        cmd.Parameters.AddWithValue("@Id", Id);
        cmd.ExecuteNonQuery();
    }

    protected virtual void Insert()
    {
        using var conn = GetConnection();
        conn.Open();
        var cmd = conn.CreateCommand();

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

    protected virtual void Update()
    {
        using var conn = GetConnection();
        conn.Open();
        var cmd = conn.CreateCommand();

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
