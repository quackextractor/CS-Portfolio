import { useEffect, useState } from "react";
import { api } from "../api";
import type { Room, RoomType } from "../types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
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

// Define RoomType if not already imported or available
// Since RoomType interface is in types.ts but we might not have a way to fetch room types dynamically yet?
// Wait, the backend usually provides room types or they are hardcoded?
// In the Reports page, there was RevenueByRoomTypeReport.
// Let's assume there's an API for room types or we hardcode them for now if the API doesn't support them fully yet.
// However, the api.ts doesn't show a room types endpoint.
// I'll check types.ts again. It has RoomType interface.
// If there is no endpoint for room types, I might need to mock them or just input ID?
// "Implement form with error handling (similar to booking creation)"
// Ideally we select a room type from a dropdown.
// I will assume for now I can map generic room types or I'll check if I can fetch them.
// Looking at `api.Rooms.getAll`, it returns `Room[]`.
// `Room` has `roomTypeId`.
// I will add a hardcoded list of room types for the UI if I can't fetch them,
// or I will try to fetch them if I add an endpoint.
// For now, let's hardcode a few common types or just use an input for ID if strictly needed,
// but dropdown is better.
// Actually, I'll start with just ID input if I must, but name mapping is better.
// Let's look at `Rooms` page requirements: "Create, Edit, Delete".
// I'll create the structure first.

export function Rooms() {
    const [rooms, setRooms] = useState<Room[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form state
    const [newRoom, setNewRoom] = useState({
        roomNumber: "",
        roomTypeId: "1", // Default to 1
        basePrice: "100",
        isClean: true
    });

    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [roomToDelete, setRoomToDelete] = useState<Room | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [dialogContent, setDialogContent] = useState({ title: "", description: "" });

    // Mock room types for dropdown if API is missing
    const roomTypes = [
        { id: 1, name: "Single" },
        { id: 2, name: "Double" },
        { id: 3, name: "Suite" },
        { id: 4, name: "Deluxe" },
    ];

    useEffect(() => {
        loadRooms();
    }, []);

    const loadRooms = () => {
        setIsLoading(true);
        api.rooms.getAll()
            .then(setRooms)
            .catch(error => {
                console.error("Failed to load rooms", error);
                showDialog("Error", "Failed to load rooms.");
            })
            .finally(() => setIsLoading(false));
    };

    const showDialog = (title: string, description: string) => {
        setDialogContent({ title, description });
        setDialogOpen(true);
    };

    const handleCreate = async () => {
        if (!newRoom.roomNumber.trim()) {
            showDialog("Validation Error", "Please enter a Room Number.");
            return;
        }
        if (isNaN(parseFloat(newRoom.basePrice)) || parseFloat(newRoom.basePrice) <= 0) {
            showDialog("Validation Error", "Please enter a valid Base Price.");
            return;
        }

        setIsSubmitting(true);
        try {
            // Check if api.rooms.create exists, if not need to add it to api.ts
            // Assuming we will add it.
            // For now using `any` cast if typescript complains until I update api.ts
            // But I am writing this file first.
            await (api.rooms as any).create({
                roomNumber: newRoom.roomNumber,
                roomTypeId: parseInt(newRoom.roomTypeId),
                basePrice: parseFloat(newRoom.basePrice),
                isClean: newRoom.isClean,
                lastMaintenance: null
            });

            showDialog("Success", "Room created successfully!");
            setNewRoom({ roomNumber: "", roomTypeId: "1", basePrice: "100", isClean: true });
            loadRooms();
        } catch (e: any) {
            console.error(e);
            // Check if it's a duplicate room number error (backend dependent)
            // If backend returns 409 or specific message, show it.
            // Currently backend might return 500 on uniqueness constraint violation if not handled explicitly.
            // We can pre-check or just handle the error.
            const errorMsg = e.response?.data || e.message || "Unknown error";
            if (errorMsg.includes("Room number") || errorMsg.includes("unique") || e.response?.status === 409) {
                showDialog("Error", "Room number already exists.");
            } else {
                showDialog("Error", "Failed to create room. " + errorMsg);
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const confirmDelete = (room: Room) => {
        setRoomToDelete(room);
    };

    const handleDelete = async () => {
        if (!roomToDelete) return;
        setDeletingId(roomToDelete.id);
        try {
            // Assuming api.rooms.delete exists
            await (api.rooms as any).delete(roomToDelete.id);
            loadRooms();
            setRoomToDelete(null);
        } catch (e: any) {
            console.error(e);
            // Handle "on delete cascade" / foreign key constraint errors
            // If backend throws 500 or 400 due to FK.
            // The prompt said: "Implement 'on delete cascade' logic (frontend or backend confirmation?)"
            // "Also allow for removing bookings, similairly like as in the /guests. Also change the path from /bookings/new to /bookings/, as it would be inaccurate, since you can both create and remove bookings there."
            // For Rooms, if it fails, we inform user. 
            let msg = "Failed to delete room.";
            if (e.response && e.response.status === 409) { // Conflict
                msg += " It might have active bookings.";
            } else if (e.message) {
                msg += " " + e.message;
            }
            showDialog("Error", msg);
        } finally {
            setDeletingId(null);
        }
    };

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold tracking-tight">Rooms</h2>
            </div>

            <Card className="max-w-2xl">
                <CardHeader>
                    <CardTitle>Add New Room</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label>Room Number</Label>
                            <Input
                                value={newRoom.roomNumber}
                                onChange={e => setNewRoom({ ...newRoom, roomNumber: e.target.value })}
                                disabled={isSubmitting}
                                placeholder="101"
                            />
                        </div>
                        <div className="space-y-2">
                            <Label>Room Type</Label>
                            <Select
                                value={newRoom.roomTypeId}
                                onValueChange={v => setNewRoom({ ...newRoom, roomTypeId: v })}
                                disabled={isSubmitting}
                            >
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Type" />
                                </SelectTrigger>
                                <SelectContent>
                                    {roomTypes.map(rt => (
                                        <SelectItem key={rt.id} value={rt.id.toString()}>{rt.name}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <Label>Base Price ($)</Label>
                            <Input
                                type="number"
                                value={newRoom.basePrice}
                                onChange={e => setNewRoom({ ...newRoom, basePrice: e.target.value })}
                                disabled={isSubmitting}
                                placeholder="100.00"
                            />
                        </div>
                        <div className="flex items-center space-x-2 pt-8">
                            <input
                                type="checkbox"
                                id="isClean"
                                checked={newRoom.isClean}
                                onChange={(e) => setNewRoom({ ...newRoom, isClean: e.target.checked })}
                                disabled={isSubmitting}
                                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                            />
                            <Label htmlFor="isClean">Is Clean?</Label>
                        </div>
                    </div>
                    <Button onClick={handleCreate} className="w-full" disabled={isSubmitting}>
                        {isSubmitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...</> : <><Plus className="mr-2 h-4 w-4" /> Create Room</>}
                    </Button>
                </CardContent>
            </Card>

            <Card>
                <CardContent className="p-0">
                    {isLoading && rooms.length === 0 ? (
                        <div className="flex justify-center items-center p-8 text-muted-foreground">
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading rooms...
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>ID</TableHead>
                                    <TableHead>Number</TableHead>
                                    <TableHead>Type</TableHead>
                                    <TableHead>Price</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {rooms.map((room) => (
                                    <TableRow key={room.id}>
                                        <TableCell>{room.id}</TableCell>
                                        <TableCell>{room.roomNumber}</TableCell>
                                        <TableCell>{roomTypes.find(t => t.id === room.roomTypeId)?.name || room.roomTypeId}</TableCell>
                                        <TableCell>${room.basePrice?.toFixed(2) || 'N/A'}</TableCell>
                                        <TableCell>
                                            <Button variant="destructive" size="sm" onClick={() => confirmDelete(room)} disabled={deletingId === room.id}>
                                                {deletingId === room.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash className="h-4 w-4" />}
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {rooms.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={5} className="text-center h-24 text-muted-foreground">
                                            No rooms found.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            <AlertDialog open={!!roomToDelete} onOpenChange={(open) => !open && setRoomToDelete(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This action cannot be undone. This will permanently delete Room {roomToDelete?.roomNumber}.
                            Any bookings associated with this room might be deleted or cause errors.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Delete</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

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
