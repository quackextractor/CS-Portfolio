import { useEffect, useState } from "react";
import { api } from "../api";
import type { Guest } from "../types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Plus, Trash, Loader2 } from "lucide-react";
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
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [guestToDelete, setGuestToDelete] = useState<Guest | null>(null);

    // Feedback dialog state
    const [dialogOpen, setDialogOpen] = useState(false);
    const [dialogContent, setDialogContent] = useState({ title: "", description: "" });

    useEffect(() => {
        loadGuests();
    }, []);

    const loadGuests = () => {
        setIsLoading(true);
        api.guests.getAll()
            .then(setGuests)
            .catch(console.error)
            .finally(() => setIsLoading(false));
    };

    const showDialog = (title: string, description: string) => {
        setDialogContent({ title, description });
        setDialogOpen(true);
    };

    const validateEmail = (email: string) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    };

    const validateDOB = (dob: string) => {
        if (!dob) return false;
        const date = new Date(dob);
        const today = new Date();
        // Check if date is valid and in the past
        return !isNaN(date.getTime()) && date < today;
    };

    const handleCreate = async () => {
        // Validation
        if (!newGuest.firstName.trim() || !newGuest.lastName.trim()) {
            showDialog("Validation Error", "Please enter both First Name and Last Name.");
            return;
        }
        if (!validateEmail(newGuest.email)) {
            showDialog("Validation Error", "Please enter a valid Email address.");
            return;
        }
        if (!validateDOB(newGuest.dateOfBirth)) {
            showDialog("Validation Error", "Please enter a valid Date of Birth (must be in the past).");
            return;
        }

        setIsSubmitting(true);
        try {
            await api.guests.create({
                ...newGuest,
                phone: "",
                isActive: true
            });
            setNewGuest({ firstName: "", lastName: "", email: "", dateOfBirth: "" });
            loadGuests();
            showDialog("Success", "Guest created successfully!");
        } catch (e: any) {
            console.error(e);
            showDialog("Error", "Failed to create guest. " + (e.message || ""));
        } finally {
            setIsSubmitting(false);
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
            setGuestToDelete(null);
        } catch (e) {
            console.error(e);
            showDialog("Error", "Failed to delete guest.");
        } finally {
            setDeletingId(null);
        }
    }

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold tracking-tight">Guests</h2>
            </div>

            <div className="">
                <Card className="max-w-2xl mx-auto">
                    <CardHeader>
                        <CardTitle>Add New Guest</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>First Name</Label>
                                <Input
                                    value={newGuest.firstName}
                                    onChange={e => setNewGuest({ ...newGuest, firstName: e.target.value })}
                                    disabled={isSubmitting}
                                    placeholder="John"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Last Name</Label>
                                <Input
                                    value={newGuest.lastName}
                                    onChange={e => setNewGuest({ ...newGuest, lastName: e.target.value })}
                                    disabled={isSubmitting}
                                    placeholder="Doe"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Email</Label>
                                <Input
                                    value={newGuest.email}
                                    onChange={e => setNewGuest({ ...newGuest, email: e.target.value })}
                                    disabled={isSubmitting}
                                    placeholder="john.doe@example.com"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Date of Birth</Label>
                                <Input
                                    type="date"
                                    value={newGuest.dateOfBirth}
                                    onChange={e => setNewGuest({ ...newGuest, dateOfBirth: e.target.value })}
                                    disabled={isSubmitting}
                                />
                            </div>
                        </div>
                        <Button onClick={handleCreate} className="w-full" disabled={isSubmitting}>
                            {isSubmitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...</> : <><Plus className="mr-2 h-4 w-4" /> Create Guest</>}
                        </Button>
                    </CardContent>
                </Card>
            </div>

            <Card className="">
                <CardContent className="p-0">
                    {isLoading && guests.length === 0 ? (
                        <div className="flex justify-center items-center p-8 text-muted-foreground">
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading guests...
                        </div>
                    ) : (
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
                                                {deletingId === guest.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash className="h-4 w-4" />}
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {guests.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                                            No guests found.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            {/* Delete Confirmation Dialog */}
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

            {/* Info/Error Alert Dialog */}
            <AlertDialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>{dialogContent.title}</AlertDialogTitle>
                        <AlertDialogDescription>
                            {dialogContent.description}
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogAction onClick={() => setDialogOpen(false)}>OK</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    );
}
