namespace Hotel.Backend.Data;

public static class DbConfig
{
    public static string ConnectionString { get; private set; } = string.Empty;

    public static void Initialize(string connectionString)
    {
        ConnectionString = connectionString;
    }
}
