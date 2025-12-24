import { useState } from "react";
import { api } from "../api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export function Import() {
    const [file, setFile] = useState<File | null>(null);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a file first.");
            return;
        }

        setLoading(true);
        setError("");
        setMessage("");

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await api.import.guests(formData);
            setMessage(`${res.Message} (${res.Count} records)`);
        } catch (err: any) {
            console.error(err);
            setError(err.response?.data || "Upload failed.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-xl mx-auto space-y-8">
            <h2 className="text-3xl font-bold tracking-tight">Import Data</h2>

            <Card>
                <CardHeader>
                    <CardTitle>Import Guests (JSON)</CardTitle>
                    <CardDescription>
                        Upload a JSON file containing a list of guests.
                        Format: [{"{ \"firstName\": \"...\", ... }"}]
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid w-full items-center gap-1.5">
                        <Label htmlFor="guest-file">Guest JSON File</Label>
                        <Input id="guest-file" type="file" accept=".json" onChange={handleFileChange} />
                    </div>

                    {error && <p className="text-sm text-red-500">{error}</p>}
                    {message && <p className="text-sm text-green-500">{message}</p>}

                    <Button onClick={handleUpload} disabled={loading || !file}>
                        {loading ? "Importing..." : "Import Guests"}
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}
