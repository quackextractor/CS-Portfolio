using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using Microsoft.Data.SqlClient;
using Microsoft.Extensions.Configuration;

namespace Hotel.Backend.Setup
{
    public static class SetupService
    {
        public static void RunSetup(IConfiguration config)
        {
            Console.WriteLine("--- Starting Setup ---");
            
            // 1. Setup Database
            SetupDatabase(config);

            // 2. Setup Frontend
            SetupFrontend();

            Console.WriteLine("\n[OK] Setup completed successfully.");
        }

        private static void SetupDatabase(IConfiguration config)
        {
            Console.WriteLine("Setting up database...");
            var connStr = config.GetConnectionString("DefaultConnection");
            if (string.IsNullOrEmpty(connStr))
            {
                 Console.WriteLine("[FAILED] Connection string 'DefaultConnection' not found in configuration.");
                 return;
            }

            // Path relative to Hotel.Backend (assuming we run from Hotel.Backend dir)
            var dbPath = Path.Combine("..", "Database");
            if (!Directory.Exists(dbPath))
            {
                 Console.WriteLine($"[WARNING] Database script directory '{dbPath}' not found.");
            }

            // Extract DB Name
            var builder = new SqlConnectionStringBuilder(connStr);
            var targetDb = builder.InitialCatalog;

            // 1. Ensure DB Exists (Local Only)
            var isLocal = builder.DataSource.Contains("(localdb)", StringComparison.OrdinalIgnoreCase) || 
                          builder.DataSource.Contains("localhost", StringComparison.OrdinalIgnoreCase) ||
                          builder.DataSource == "." ||
                          builder.DataSource.Contains("127.0.0.1");

            if (isLocal)
            {
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
            }
            else
            {
                Console.WriteLine($"[INFO] Remote server detected ('{builder.DataSource}'). Skipping automatic database creation. Using existing database '{targetDb}'.");
            }


            // 2. Run Scripts
            if (Directory.Exists(dbPath))
            {
                try
                {
                    using (var conn = new SqlConnection(connStr))
                    {
                        conn.Open();
                        
                        var scripts = Directory.GetFiles(dbPath, "*.sql").OrderBy(f => f).ToList();
                        if (scripts.Count == 0)
                        {
                            Console.WriteLine("[INFO] No SQL scripts found to execute.");
                        }

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
        }

        private static void SetupFrontend()
        {
            Console.WriteLine("Setting up Frontend (npm install)...");
            var fePath = Path.Combine("..", "Hotel.Frontend");
            
            RunProcess("npm", "install", fePath);
        }

        private static void RunProcess(string fileName, string args, string workingDir)
        {
            if (!Directory.Exists(workingDir))
            {
                 Console.WriteLine($"[WARNING] Directory {workingDir} not found.");
                 return;
            }

            // Windows npm fix
            if (fileName == "npm" && System.Runtime.InteropServices.RuntimeInformation.IsOSPlatform(System.Runtime.InteropServices.OSPlatform.Windows))
            {
                fileName = "cmd";
                args = $"/c npm {args}";
            }

            var pi = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = args,
                WorkingDirectory = workingDir,
                UseShellExecute = false,
                RedirectStandardOutput = true, 
                RedirectStandardError = true
            };

            try
            {
                var p = Process.Start(pi);
                if (p != null)
                {
                    p.OutputDataReceived += (sender, e) => { if (e.Data != null) Console.WriteLine(e.Data); };
                    p.ErrorDataReceived += (sender, e) => { if (e.Data != null) Console.WriteLine(e.Data); };
                    p.BeginOutputReadLine();
                    p.BeginErrorReadLine();
                    p.WaitForExit();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[FAILED] Could not run {fileName}: {ex.Message}");
            }
        }
    }
}
