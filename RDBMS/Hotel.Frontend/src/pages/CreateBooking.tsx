import { useEffect, useState } from "react";
import { api } from "../api";
import type { Guest, Room } from "../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export function CreateBooking() {
    const [guests, setGuests] = useState<Guest[]>([]);
    const [rooms, setRooms] = useState<Room[]>([]);


    const [isLoading, setIsLoading] = useState(true);
    const [loadingProgress, setLoadingProgress] = useState(0);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [selectedGuest, setSelectedGuest] = useState("");
    const [selectedRoom, setSelectedRoom] = useState("");
    const [checkIn, setCheckIn] = useState("");
    const [checkOut, setCheckOut] = useState("");
    const [dialogOpen, setDialogOpen] = useState(false);
    const [dialogContent, setDialogContent] = useState({ title: "", description: "" });

    useEffect(() => {
        const loadData = async () => {
            setIsLoading(true);
            setLoadingProgress(10); // Start progress
            try {
                const [guestsData, roomsData] = await Promise.all([
                    api.guests.getAll().then(res => { setLoadingProgress(prev => prev + 30); return res; }),
                    api.rooms.getAll().then(res => { setLoadingProgress(prev => prev + 30); return res; })
                ]);

                setGuests(guestsData);
                setRooms(roomsData);
            } catch (error) {
                console.error("Failed to load data", error);
            } finally {
                setLoadingProgress(100);
                setTimeout(() => setIsLoading(false), 500); // Small delay to show completion
            }
        };

        loadData();
    }, []);

    const showDialog = (title: string, description: string) => {
        setDialogContent({ title, description });
        setDialogOpen(true);
    };

    const handleSubmit = async () => {
        if (!selectedGuest || !selectedRoom || !checkIn || !checkOut) {
            showDialog("Validation Error", "Please fill all fields");
            return;
        }

        setIsSubmitting(true);
        try {
            await api.bookings.create({
                guestId: parseInt(selectedGuest),
                roomId: parseInt(selectedRoom),
                checkIn,
                checkOut,
                checkOut
            });
            showDialog("Success", "Booking Created Successfully!");
            // Reset form or redirect
            setSelectedGuest("");
            setSelectedRoom("");
            setCheckIn("");
            setCheckOut("");
        } catch (e: any) {
            console.error(e);
            showDialog("Error", "Error creating booking: " + (e.response?.data || e.message));
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Card className="max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle>Create New Booking</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {isLoading ? (
                    <div className="space-y-2">
                        <Label>Loading resources...</Label>
                        <Progress value={loadingProgress} className="w-full" />
                    </div>
                ) : (
                    <>
                        <div className="space-y-2">
                            <Label>Guest</Label>
                            <Select onValueChange={setSelectedGuest} value={selectedGuest} disabled={isLoading || isSubmitting}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Guest" />
                                </SelectTrigger>
                                <SelectContent>
                                    {guests.map(g => (
                                        <SelectItem key={g.id} value={g.id.toString()}>{g.firstName} {g.lastName}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="space-y-2">
                            <Label>Room</Label>
                            <Select onValueChange={setSelectedRoom} value={selectedRoom} disabled={isLoading || isSubmitting}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select Room" />
                                </SelectTrigger>
                                <SelectContent>
                                    {rooms.map(r => (
                                        <SelectItem key={r.id} value={r.id.toString()}>{r.roomNumber}</SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Check-in</Label>
                                <Input type="date" value={checkIn} onChange={e => setCheckIn(e.target.value)} disabled={isLoading || isSubmitting} />
                            </div>
                            <div className="space-y-2">
                                <Label>Check-out</Label>
                                <Input type="date" value={checkOut} onChange={e => setCheckOut(e.target.value)} disabled={isLoading || isSubmitting} />
                            </div>
                        </div>



                        <Button className="w-full" onClick={handleSubmit} disabled={isLoading || isSubmitting}>
                            {isSubmitting ? "Creating Booking..." : "Create Booking"}
                        </Button>
                    </>
                )}
            </CardContent>

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
        </Card>
    );
}
