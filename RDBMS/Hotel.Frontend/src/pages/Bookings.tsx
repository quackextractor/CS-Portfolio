import { useEffect, useState } from "react";
import { api } from "../api";
import type { Guest, Room, Booking, Service, BookingService } from "../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Trash, Loader2, Plus } from "lucide-react";
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

export function Bookings() {
    const [guests, setGuests] = useState<Guest[]>([]);
    const [rooms, setRooms] = useState<Room[]>([]);
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [services, setServices] = useState<Service[]>([]);

    const [isLoading, setIsLoading] = useState(true);
    const [loadingProgress, setLoadingProgress] = useState(0);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Form state
    const [selectedGuest, setSelectedGuest] = useState("");
    const [selectedRoom, setSelectedRoom] = useState("");
    const [checkIn, setCheckIn] = useState("");
    const [checkOut, setCheckOut] = useState("");
    const [selectedServices, setSelectedServices] = useState<number[]>([]);

    // Feedback
    const [dialogOpen, setDialogOpen] = useState(false);
    const [dialogContent, setDialogContent] = useState({ title: "", description: "" });
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [bookingToDelete, setBookingToDelete] = useState<Booking | null>(null);

    // Details View
    const [selectedDetails, setSelectedDetails] = useState<{ booking: Booking, services: BookingService[] } | null>(null);
    const [detailsLoading, setDetailsLoading] = useState(false);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setIsLoading(true);
        setLoadingProgress(10);
        try {
            const [guestsData, roomsData, bookingsData, servicesData] = await Promise.all([
                api.guests.getAll().then(res => { setLoadingProgress(prev => prev + 20); return res; }),
                api.rooms.getAll().then(res => { setLoadingProgress(prev => prev + 20); return res; }),
                api.bookings.getAll().then(res => { setLoadingProgress(prev => prev + 20); return res; }),
                api.services.getAll().then(res => { setLoadingProgress(prev => prev + 20); return res; })
            ]);

            setGuests(guestsData);
            setRooms(roomsData);
            setBookings(bookingsData);
            setServices(servicesData);
        } catch (error) {
            console.error("Failed to load data", error);
            showDialog("Error", "Failed to load inputs.");
        } finally {
            setLoadingProgress(100);
            setTimeout(() => setIsLoading(false), 500);
        }
    };

    const showDialog = (title: string, description: string) => {
        setDialogContent({ title, description });
        setDialogOpen(true);
    };

    const handleSubmit = async () => {
        if (!selectedGuest || !selectedRoom || !checkIn || !checkOut) {
            showDialog("Validation Error", "Please fill all fields");
            return;
        }

        // Basic date validation
        if (new Date(checkIn) >= new Date(checkOut)) {
            showDialog("Validation Error", "Check-out date must be after check-in date.");
            return;
        }

        setIsSubmitting(true);
        try {
            await api.bookings.create({
                guestId: parseInt(selectedGuest),
                roomId: parseInt(selectedRoom),
                checkIn,
                checkOut,
                serviceIds: selectedServices
            });
            showDialog("Success", "Booking Created Successfully!");

            // Reset form
            setSelectedGuest("");
            setSelectedRoom("");
            setCheckIn("");
            setCheckOut("");
            setSelectedServices([]);

            // Reload bookings to show new one
            api.bookings.getAll().then(setBookings);
        } catch (e: any) {
            console.error(e);
            showDialog("Error", "Error creating booking: " + (e.response?.data || e.message));
        } finally {
            setIsSubmitting(false);
        }
    };

    const confirmDelete = (e: React.MouseEvent, booking: Booking) => {
        e.stopPropagation();
        setBookingToDelete(booking);
    }

    const handleDelete = async () => {
        if (!bookingToDelete) return;
        setDeletingId(bookingToDelete.id);
        try {
            await api.bookings.delete(bookingToDelete.id);
            // Refresh list
            const updated = bookings.filter(b => b.id !== bookingToDelete.id);
            setBookings(updated);
            setBookingToDelete(null);
        } catch (e: any) {
            console.error(e);
            showDialog("Error", "Failed to delete booking.");
        } finally {
            setDeletingId(null);
        }
    }

    const handleViewDetails = async (id: number) => {
        setDetailsLoading(true);
        try {
            const details = await api.bookings.get(id);
            setSelectedDetails(details);
        } catch (e) {
            console.error(e);
            showDialog("Error", "Failed to load booking details.");
        } finally {
            setDetailsLoading(false);
        }
    }

    // specific helpers for display
    const getGuestName = (id: number) => {
        const g = guests.find(x => x.id === id);
        return g ? `${g.firstName} ${g.lastName}` : `ID: ${id}`;
    };

    const getRoomNumber = (id: number) => {
        const r = rooms.find(x => x.id === id);
        return r ? r.roomNumber : `ID: ${id}`;
    };

    const getServiceName = (id: number) => {
        const s = services.find(x => x.id === id);
        return s ? s.name : `ID: ${id}`;
    }

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            <div className="flex justify-between items-center">
                <h2 className="text-3xl font-bold tracking-tight">Bookings</h2>
            </div>

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

                            <div className="space-y-2">
                                <Label>Extra Services</Label>
                                <div className="grid grid-cols-2 gap-2 border p-4 rounded-md">
                                    {services.map(service => (
                                        <div key={service.id} className="flex items-center space-x-2">
                                            <input
                                                type="checkbox"
                                                id={`service-${service.id}`}
                                                className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                                                checked={selectedServices.includes(service.id)}
                                                onChange={(e) => {
                                                    if (e.target.checked) {
                                                        setSelectedServices(prev => [...prev, service.id]);
                                                    } else {
                                                        setSelectedServices(prev => prev.filter(id => id !== service.id));
                                                    }
                                                }}
                                                disabled={isLoading || isSubmitting}
                                            />
                                            <label
                                                htmlFor={`service-${service.id}`}
                                                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                                            >
                                                {service.name} (${service.price})
                                            </label>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <Button className="w-full" onClick={handleSubmit} disabled={isLoading || isSubmitting}>
                                {isSubmitting ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...</> : <><Plus className="mr-2 h-4 w-4" /> Create Booking</>}
                            </Button>
                        </>
                    )}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Existing Bookings</CardTitle>
                </CardHeader>
                <CardContent>
                    {isLoading && bookings.length === 0 ? (
                        <div className="flex justify-center items-center p-8 text-muted-foreground">
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading bookings...
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>ID</TableHead>
                                    <TableHead>Guest</TableHead>
                                    <TableHead>Room</TableHead>
                                    <TableHead>Dates</TableHead>
                                    <TableHead>Total Price</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {bookings.map((b) => (
                                    <TableRow
                                        key={b.id}
                                        className="cursor-pointer hover:bg-muted/50"
                                        onClick={() => handleViewDetails(b.id)}
                                    >
                                        <TableCell>{b.id}</TableCell>
                                        <TableCell>{getGuestName(b.guestId)}</TableCell>
                                        <TableCell>{getRoomNumber(b.roomId)}</TableCell>
                                        <TableCell>
                                            {new Date(b.checkIn).toLocaleDateString()} - {new Date(b.checkOut).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell>${b.totalPrice?.toFixed(2)}</TableCell>
                                        <TableCell>
                                            <Button variant="destructive" size="sm" onClick={(e) => confirmDelete(e, b)} disabled={deletingId === b.id}>
                                                {deletingId === b.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash className="h-4 w-4" />}
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {bookings.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={6} className="text-center h-24 text-muted-foreground">
                                            No bookings found.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>

            <AlertDialog open={!!bookingToDelete} onOpenChange={(open) => !open && setBookingToDelete(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This action cannot be undone. This will permanently delete Booking #{bookingToDelete?.id}.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleDelete} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">Delete</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>

            <AlertDialog open={!!selectedDetails || detailsLoading} onOpenChange={(open) => !open && !detailsLoading && setSelectedDetails(null)}>
                <AlertDialogContent className="max-w-xl">
                    {detailsLoading ? (
                        <div className="flex flex-col justify-center items-center p-8 space-y-4">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                            <p>Loading details...</p>
                        </div>
                    ) : selectedDetails ? (
                        <>
                            <AlertDialogHeader>
                                <AlertDialogTitle>Booking Details #{selectedDetails.booking.id}</AlertDialogTitle>
                            </AlertDialogHeader>

                            <div className="space-y-4 py-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <Label className="text-muted-foreground">Guest</Label>
                                        <div className="font-medium">{getGuestName(selectedDetails.booking.guestId)}</div>
                                    </div>
                                    <div>
                                        <Label className="text-muted-foreground">Room</Label>
                                        <div className="font-medium">{getRoomNumber(selectedDetails.booking.roomId)}</div>
                                    </div>
                                    <div>
                                        <Label className="text-muted-foreground">Check-in</Label>
                                        <div className="font-medium">{new Date(selectedDetails.booking.checkIn).toLocaleDateString()}</div>
                                    </div>
                                    <div>
                                        <Label className="text-muted-foreground">Check-out</Label>
                                        <div className="font-medium">{new Date(selectedDetails.booking.checkOut).toLocaleDateString()}</div>
                                    </div>
                                </div>

                                <div>
                                    <Label className="text-muted-foreground mb-2 block">Services</Label>
                                    {selectedDetails.services.length > 0 ? (
                                        <div className="border rounded-md divide-y">
                                            {selectedDetails.services.map(s => (
                                                <div key={s.id} className="p-2 flex justify-between text-sm">
                                                    <span>{getServiceName(s.serviceId)}</span>
                                                    <span>${s.subTotal?.toFixed(2)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-sm text-muted-foreground">No services for this booking.</div>
                                    )}
                                </div>

                                <div className="flex justify-between items-center border-t pt-4">
                                    <span className="font-bold text-lg">Total Price</span>
                                    <span className="font-bold text-lg">${selectedDetails.booking.totalPrice?.toFixed(2)}</span>
                                </div>
                            </div>

                            <AlertDialogFooter>
                                <AlertDialogCancel onClick={() => setSelectedDetails(null)}>Close</AlertDialogCancel>
                            </AlertDialogFooter>
                        </>
                    ) : null}
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
