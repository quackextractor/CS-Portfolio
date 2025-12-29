import { useEffect, useState } from "react";
import { api } from "../api";
import type { Room } from "../types";
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

export function Rooms() {
    const [rooms, setRooms] = useState<Room[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);

    // Form state
    // Form state
    const [newRoom, setNewRoom] = useState({
        roomNumber: "",
        roomTypeId: "1" // Default to 1
    });

    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [roomToDelete, setRoomToDelete] = useState<Room | null>(null);
    const [dialogOpen, setDialogContent] = useState<any>({ open: false, title: "", description: "" });

    // Mock room types for dropdown if API is missing
    const roomTypes = [
        { id: 1, name: "Single", price: 100 },
        { id: 2, name: "Double", price: 150 },
        { id: 3, name: "Suite", price: 300 },
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
        setDialogContent({ open: true, title, description });
    };

    const handleCreateOrUpdate = async () => {
        if (!newRoom.roomNumber.trim()) {
            showDialog("Validation Error", "Please enter a Room Number.");
            return;
        }

        setIsSubmitting(true);
        try {
            if (editingId) {
                // Update
                await api.rooms.update(editingId, {
                    id: editingId,
                    roomNumber: newRoom.roomNumber,
                    roomTypeId: parseInt(newRoom.roomTypeId)
                });
                showDialog("Success", "Room updated successfully!");
            } else {
                // Create
                await api.rooms.create({
                    roomNumber: newRoom.roomNumber,
                    roomTypeId: parseInt(newRoom.roomTypeId)
                });
                showDialog("Success", "Room created successfully!");
            }

            // Reset
            setNewRoom({ roomNumber: "", roomTypeId: "1" });
            setEditingId(null);

            loadRooms();
        } catch (e: any) {
            console.error(e);

            const errorMsg = e.response?.data || e.message;
            if (e.response?.status === 409) {
                showDialog("Error", e.response.data || "Room number already exists.");
            } else {
                showDialog("Error", `Failed to ${editingId ? "update" : "create"} room. ` + errorMsg);
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const startEdit = (room: Room) => {
        setNewRoom({
            roomNumber: room.roomNumber,
            roomTypeId: room.roomTypeId.toString()
        });
        setEditingId(room.id);
    };

    const cancelEdit = () => {
        setNewRoom({ roomNumber: "", roomTypeId: "1" });
        setEditingId(null);
    };

    const confirmDelete = (room: Room) => {
        setRoomToDelete(room);
    };

    const handleDelete = async () => {
        if (!roomToDelete) return;
        setDeletingId(roomToDelete.id);
        try {
            await (api.rooms as any).delete(roomToDelete.id);
            loadRooms();
            setRoomToDelete(null);
        } catch (e: any) {
            console.error(e);
            if (e.response && e.response.status === 409) {
                showDialog("Error", e.response.data || "Failed to delete room (Conflict).");
            } else {
                showDialog("Error", "Failed to delete room.");
            }
        } finally {
            setDeletingId(null);
        }
    };

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold tracking-tight">Rooms</h2>
            </div>

            <Card className="max-w-2xl mx-auto">
                <CardHeader>
                    <CardTitle>{editingId ? "Edit Room" : "Add New Room"}</CardTitle>
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
                                        <SelectItem key={rt.id} value={rt.id.toString()}>
                                            {rt.name} (${rt.price})
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                    </div>
                    <div className="flex gap-2 mt-4">
                        <Button onClick={handleCreateOrUpdate} className="flex-1" disabled={isSubmitting}>
                            {isSubmitting ?
                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> {editingId ? "Updating..." : "Creating..."}</> :
                                <>{editingId ? "Update Room" : <><Plus className="mr-2 h-4 w-4" /> Create Room</>}</>
                            }
                        </Button>
                        {editingId && (
                            <Button variant="outline" onClick={cancelEdit} disabled={isSubmitting}>
                                Cancel
                            </Button>
                        )}
                    </div>
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
                                {rooms.map((room) => {
                                    const rType = roomTypes.find(t => t.id === room.roomTypeId);
                                    return (
                                        <TableRow key={room.id}>
                                            <TableCell>{room.id}</TableCell>
                                            <TableCell>{room.roomNumber}</TableCell>
                                            <TableCell>{rType?.name || room.roomTypeId}</TableCell>
                                            <TableCell>${rType?.price.toFixed(2) || 'N/A'}</TableCell>
                                            <TableCell className="flex gap-2">
                                                <Button variant="outline" size="sm" onClick={() => startEdit(room)} disabled={!!deletingId || !!editingId}>
                                                    Edit
                                                </Button>
                                                <Button variant="destructive" size="sm" onClick={() => confirmDelete(room)} disabled={deletingId === room.id || !!editingId}>
                                                    {deletingId === room.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash className="h-4 w-4" />}
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
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

            <AlertDialog open={dialogOpen.open} onOpenChange={(open) => setDialogContent({ ...dialogOpen, open })}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>{dialogOpen.title}</AlertDialogTitle>
                        <AlertDialogDescription>
                            {dialogOpen.description}
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogAction onClick={() => setDialogContent({ ...dialogOpen, open: false })}>OK</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

        </div>
    );
}
