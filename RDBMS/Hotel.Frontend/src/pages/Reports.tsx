import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { api } from "../api";
import type { GuestBookingReport, RoomAvailabilityReport, ServiceUsageStatsReport, RevenueByRoomTypeReport } from "../types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Reports() {
    const [bookings, setBookings] = useState<GuestBookingReport[]>([]);
    const [availability, setAvailability] = useState<RoomAvailabilityReport[]>([]);
    const [serviceStats, setServiceStats] = useState<ServiceUsageStatsReport[]>([]);
    const [revenueStats, setRevenueStats] = useState<RevenueByRoomTypeReport[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const loadReports = async () => {
            setIsLoading(true);
            try {
                await Promise.all([
                    api.reports.guestBookings().then(setBookings),
                    api.reports.availability().then(setAvailability),
                    api.reports.serviceStats().then(setServiceStats),
                    api.reports.revenueByRoomType().then(setRevenueStats)
                ]);
            } catch (error) {
                console.error("Failed to load reports", error);
            } finally {
                setIsLoading(false);
            }
        };

        loadReports();
    }, []);

    if (isLoading) {
        return (
            <div className="flex justify-center items-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <span className="ml-2 text-lg text-muted-foreground">Loading reports...</span>
            </div>
        );
    }

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
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




            <Card>
                <CardHeader>
                    <CardTitle>Revenue by Room Type (Aggregated from 3 tables)</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Room Type</TableHead>
                                <TableHead>Total Bookings</TableHead>
                                <TableHead>Total Revenue</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {revenueStats.map((r) => (
                                <TableRow key={r.roomTypeName}>
                                    <TableCell>{r.roomTypeName}</TableCell>
                                    <TableCell>{r.totalBookings}</TableCell>
                                    <TableCell>${r.totalRevenue}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div >
    );
}
