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

    const handleUpload = async (type: 'guests' | 'services') => {
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
            let res;
            if (type === 'guests') {
                res = await api.import.guests(formData);
            } else {
                res = await api.import.services(formData);
            }
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
                    <CardTitle>Import Files (JSON)</CardTitle>
                    <CardDescription>
                        Import Guests: [{"{ \"firstName\": \"...\", ... }"}] <br />
                        Import Services: [{"{ \"name\": \"...\", \"price\": 10.0 }"}]
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid w-full items-center gap-1.5">
                        <Label htmlFor="import-file">JSON File</Label>
                        <Input id="import-file" type="file" accept=".json" onChange={handleFileChange} />
                    </div>

                    <div className="flex gap-4">
                        <Button onClick={() => handleUpload('guests')} disabled={loading || !file} variant="outline">
                            Import Guests
                        </Button>
                        <Button onClick={() => handleUpload('services')} disabled={loading || !file}>
                            Import Services
                        </Button>
                    </div>

                    {error && <p className="text-sm text-red-500">{error}</p>}
                    {message && <p className="text-sm text-green-500">{message}</p>}
                </CardContent>
            </Card>
        </div>
    );
}
