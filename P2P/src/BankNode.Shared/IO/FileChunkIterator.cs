using System.Collections.Generic;
using System.IO;

namespace BankNode.Shared.IO
{
    public class FileChunkIterator
    {
        private readonly string _filePath;

        public FileChunkIterator(string filePath)
        {
            _filePath = filePath;
        }

        public IEnumerable<string> ReadChuncked()
        {
            if (!File.Exists(_filePath))
            {
                yield break;
            }

            using (var fileStream = File.OpenRead(_filePath))
            using (var streamReader = new StreamReader(fileStream))
            {
                string? line;
                while ((line = streamReader.ReadLine()) != null)
                {
                    if (!string.IsNullOrWhiteSpace(line))
                    {
                        yield return line;
                    }
                }
            }
        }
    }
}
