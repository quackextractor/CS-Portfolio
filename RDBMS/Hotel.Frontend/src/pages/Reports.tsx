import { useEffect, useState } from "react";
import { api } from "../api";
import type { GuestBookingReport, RoomAvailabilityReport } from "../types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Reports() {
    const [bookings, setBookings] = useState<GuestBookingReport[]>([]);
    const [availability, setAvailability] = useState<RoomAvailabilityReport[]>([]);

    useEffect(() => {
        api.reports.guestBookings().then(setBookings).catch(console.error);
        api.reports.availability().then(setAvailability).catch(console.error);
    }, []);

    return (
        <div className="space-y-8">
            <h2 className="text-3xl font-bold tracking-tight">Reports</h2>

            <Card>
                <CardHeader>
                    <CardTitle>Guest Bookings</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Booking ID</TableHead>
                                <TableHead>Guest</TableHead>
                                <TableHead>Room</TableHead>
                                <TableHead>Check-in</TableHead>
                                <TableHead>Check-out</TableHead>
                                <TableHead>Status</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {bookings.map((b) => (
                                <TableRow key={b.bookingId}>
                                    <TableCell>{b.bookingId}</TableCell>
                                    <TableCell>{b.firstName} {b.lastName}</TableCell>
                                    <TableCell>{b.roomNumber}</TableCell>
                                    <TableCell>{new Date(b.checkIn).toLocaleDateString()}</TableCell>
                                    <TableCell>{new Date(b.checkOut).toLocaleDateString()}</TableCell>
                                    <TableCell>{b.status}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Room Availability (Clean Rooms)</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Room ID</TableHead>
                                <TableHead>Number</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Base Price</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {availability.map((r) => (
                                <TableRow key={r.roomId}>
                                    <TableCell>{r.roomId}</TableCell>
                                    <TableCell>{r.roomNumber}</TableCell>
                                    <TableCell>{r.roomType}</TableCell>
                                    <TableCell>${r.basePrice}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
