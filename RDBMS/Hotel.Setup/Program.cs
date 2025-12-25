using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;

namespace Hotel.Setup
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                PrintHelp();
                return;
            }

            var command = args[0].ToLower();

            try
            {
                var builder = new ConfigurationBuilder()
                    .SetBasePath(Directory.GetCurrentDirectory())
                    .AddJsonFile("config.json", optional: false, reloadOnChange: true);

                IConfiguration config = builder.Build();

                switch (command)
                {
                    case "setup":
                        RunSetup(config);
                        break;
                    case "run-backend":
                        RunBackend(config);
                        break;
                    case "run-frontend":
                        RunFrontend(config);
                        break;
                    default:
                        Console.WriteLine($"Unknown command: {command}");
                        PrintHelp();
                        break;
                }
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"Error: {ex.Message}");
                Console.ResetColor();
            }
        }

        static void PrintHelp()
        {
            Console.WriteLine("Usage:");
            Console.WriteLine("  Hotel.Setup setup        - Configures DB and installs dependencies");
            Console.WriteLine("  Hotel.Setup run-backend  - Runs the Backend API");
            Console.WriteLine("  Hotel.Setup run-frontend - Runs the Frontend App");
        }

        static void RunSetup(IConfiguration config)
        {
            Console.WriteLine("--- Starting Setup ---");
            
            // 1. Update Backend Config
            UpdateBackendConfig(config);

            // 2. Setup Database
            SetupDatabase(config);

            // 3. Setup Frontend
            SetupFrontend();

            Console.WriteLine("\n[OK] Setup completed successfully.");
        }

        static void UpdateBackendConfig(IConfiguration config)
        {
            Console.WriteLine("Updating Backend configuration...");
            var backendPath = "Hotel.Backend";
            
            var configPath = Path.Combine(backendPath, "appsettings.json");
            
            if (!File.Exists(configPath))
            {
                Console.WriteLine($"[WARNING] {configPath} not found.");
                return;
            }

            try
            {
                var json = File.ReadAllText(configPath);
                
                var doc = System.Text.Json.Nodes.JsonNode.Parse(json);
                if (doc != null)
                {
                    var connStr = config.GetConnectionString("DefaultConnection");
                    if (doc["ConnectionStrings"] == null)
                    {
                        doc["ConnectionStrings"] = new System.Text.Json.Nodes.JsonObject();
                    }
                    doc["ConnectionStrings"]!["DefaultConnection"] = connStr;
                    
                    File.WriteAllText(configPath, doc.ToJsonString(new JsonSerializerOptions { WriteIndented = true }));
                    Console.WriteLine("[OK] Backend configuration updated.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[FAILED] Could not update backend config: {ex.Message}");
            }
        }

        static void SetupDatabase(IConfiguration config)
        {
            Console.WriteLine("Setting up database...");
            var connStr = config.GetConnectionString("DefaultConnection");
            var dbPath = "Database";

            // Extract DB Name
            var builder = new SqlConnectionStringBuilder(connStr);
            var targetDb = builder.InitialCatalog;

            // 1. Ensure DB Exists
            try
            {
                // Connect to master
                builder.InitialCatalog = "master";
                using (var conn = new SqlConnection(builder.ConnectionString))
                {
                    conn.Open();
                    var cmdToCheck = new SqlCommand($"SELECT database_id FROM sys.databases WHERE Name = '{targetDb}'", conn);
                    var output = cmdToCheck.ExecuteScalar();
                    
                    if (output == null)
                    {
                        Console.WriteLine($"Database '{targetDb}' does not exist. Creating...");
                        var cmdCreate = new SqlCommand($"CREATE DATABASE [{targetDb}]", conn);
                        cmdCreate.ExecuteNonQuery();
                        Console.WriteLine($"Database '{targetDb}' created.");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[WARNING] Could not check/create database: {ex.Message}. Attempting to proceed with default connection...");
            }

            // 2. Run Scripts
            try
            {
                using (var conn = new SqlConnection(connStr))
                {
                    conn.Open();
                    
                    var scripts = Directory.GetFiles(dbPath, "*.sql").OrderBy(f => f).ToList();
                    foreach (var scriptPath in scripts)
                    {
                        Console.WriteLine($"Executing {Path.GetFileName(scriptPath)}...");
                        var scriptContent = File.ReadAllText(scriptPath);
                        
                        // Split by GO
                        var batches = Regex.Split(scriptContent, @"^\s*GO\s*$", RegexOptions.Multiline | RegexOptions.IgnoreCase);
                        
                        foreach (var batch in batches)
                        {
                            if (string.IsNullOrWhiteSpace(batch)) continue;
                            using (var cmd = new SqlCommand(batch, conn))
                            {
                                cmd.ExecuteNonQuery();
                            }
                        }
                    }
                }
                Console.WriteLine("[OK] Database setup complete.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[FAILED] Database setup failed: {ex.Message}");
            }
        }

        static void SetupFrontend()
        {
            Console.WriteLine("Setting up Frontend...");
            var fePath = "Hotel.Frontend";
            
            RunProcess("npm", "install", fePath);
        }

        static void RunBackend(IConfiguration config)
        {
            Console.WriteLine("Starting Backend...");
            var bePath = "Hotel.Backend";
            RunProcess("dotnet", "run", bePath);
        }

        static void RunFrontend(IConfiguration config)
        {
            Console.WriteLine("Starting Frontend...");
            var fePath = "Hotel.Frontend";
            RunProcess("npm", "run dev", fePath);
        }

        static void RunProcess(string fileName, string args, string workingDir)
        {
            if (!Directory.Exists(workingDir))
            {
                 Console.WriteLine($"[WARNING] Directory {workingDir} not found.");
                 return;
            }

            // Windows npm fix
            if (fileName == "npm" && System.Runtime.InteropServices.RuntimeInformation.IsOSPlatform(System.Runtime.InteropServices.OSPlatform.Windows))
            {
                fileName = "npm.cmd";
            }

            var pi = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = args,
                WorkingDirectory = workingDir,
                UseShellExecute = false,
                RedirectStandardOutput = false, // Let it stream to console
                RedirectStandardError = false
            };

            try
            {
                var p = Process.Start(pi);
                if (p != null) p.WaitForExit();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[FAILED] Could not run {fileName}: {ex.Message}");
            }
        }
    }
}
