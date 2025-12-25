import { useEffect, useState } from "react";
import { api } from "../api";
import type { Guest } from "../types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Trash } from "lucide-react";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export function GuestList() {
    const [guests, setGuests] = useState<Guest[]>([]);
    const [newGuest, setNewGuest] = useState({ firstName: "", lastName: "", email: "", dateOfBirth: "" });
    const [isCreating, setIsCreating] = useState(false);
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [guestToDelete, setGuestToDelete] = useState<Guest | null>(null);

    useEffect(() => {
        loadGuests();
    }, []);

    const loadGuests = () => {
        api.guests.getAll().then(setGuests).catch(console.error);
    };

    const handleCreate = async () => {
        if (!newGuest.firstName || !newGuest.lastName) return;
        setIsCreating(true);
        try {
            await api.guests.create({
                ...newGuest,
                phone: "",
                isActive: true,
                type: 0,
                loyaltyPoints: 0
            });
            setNewGuest({ firstName: "", lastName: "", email: "", dateOfBirth: "" });
            loadGuests();
        } catch (e) {
            console.error(e);
            alert("Failed to create guest");
        } finally {
            setIsCreating(false);
        }
    };

    const confirmDelete = (guest: Guest) => {
        setGuestToDelete(guest);
    };

    const handleDelete = async () => {
        if (!guestToDelete) return;
        setDeletingId(guestToDelete.id);
        try {
            await api.guests.delete(guestToDelete.id);
            loadGuests();
        } catch (e) {
            console.error(e);
            alert("Failed to delete guest");
        } finally {
            setDeletingId(null);
            setGuestToDelete(null);
        }
    }

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold tracking-tight">Guests</h2>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader>
                        <CardTitle>Add New Guest</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label>First Name</Label>
                            <Input value={newGuest.firstName} onChange={e => setNewGuest({ ...newGuest, firstName: e.target.value })} disabled={isCreating} />
                        </div>
                        <div className="space-y-2">
                            <Label>Last Name</Label>
                            <Input value={newGuest.lastName} onChange={e => setNewGuest({ ...newGuest, lastName: e.target.value })} disabled={isCreating} />
                        </div>
                        <div className="space-y-2">
                            <Label>Email</Label>
                            <Input value={newGuest.email} onChange={e => setNewGuest({ ...newGuest, email: e.target.value })} disabled={isCreating} />
                        </div>
                        <div className="space-y-2">
                            <Label>Date of Birth</Label>
                            <Input type="date" value={newGuest.dateOfBirth} onChange={e => setNewGuest({ ...newGuest, dateOfBirth: e.target.value })} disabled={isCreating} />
                        </div>
                        <Button onClick={handleCreate} className="w-full" disabled={isCreating}>{isCreating ? "Creating..." : <><Plus className="mr-2 h-4 w-4" /> Create Guest</>}</Button>
                    </CardContent>
                </Card>
            </div>

            <div className="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>ID</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Email</TableHead>
                            <TableHead>DOB</TableHead>
                            <TableHead>Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {guests.map((guest) => (
                            <TableRow key={guest.id}>
                                <TableCell>{guest.id}</TableCell>
                                <TableCell>{guest.firstName} {guest.lastName}</TableCell>
                                <TableCell>{guest.email}</TableCell>
                                <TableCell>{new Date(guest.dateOfBirth).toLocaleDateString()}</TableCell>
                                <TableCell>
                                    <Button variant="destructive" size="sm" onClick={() => confirmDelete(guest)} disabled={deletingId === guest.id}>
                                        {deletingId === guest.id ? "..." : <Trash className="h-4 w-4" />}
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>

            <AlertDialog open={!!guestToDelete} onOpenChange={(open) => !open && setGuestToDelete(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This action cannot be undone. This will permanently delete the guest
                            {guestToDelete && <b> {guestToDelete.firstName} {guestToDelete.lastName}</b>}.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Delete</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
