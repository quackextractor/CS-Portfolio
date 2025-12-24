import { useEffect, useState } from "react";
import { api } from "../api";
import { Guest, Room, Service } from "../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";

export function CreateBooking() {
    const [guests, setGuests] = useState<Guest[]>([]);
    const [rooms, setRooms] = useState<Room[]>([]);
    const [services, setServices] = useState<Service[]>([]);

    const [selectedGuest, setSelectedGuest] = useState("");
    const [selectedRoom, setSelectedRoom] = useState("");
    const [checkIn, setCheckIn] = useState("");
    const [checkOut, setCheckOut] = useState("");
    const [selectedServices, setSelectedServices] = useState<string[]>([]);

    useEffect(() => {
        api.guests.getAll().then(setGuests).catch(console.error);
        api.rooms.getAll().then(setRooms).catch(console.error);
        api.services.getAll().then(setServices).catch(console.error);
    }, []);

    const handleSubmit = async () => {
        if (!selectedGuest || !selectedRoom || !checkIn || !checkOut) {
            alert("Please fill all fields");
            return;
        }

        try {
            await api.bookings.create({
                guestId: parseInt(selectedGuest),
                roomId: parseInt(selectedRoom),
                checkIn,
                checkOut,
                serviceIds: selectedServices.map(id => parseInt(id))
            });
            alert("Booking Created Successfully!");
            // Reset form or redirect
            setSelectedGuest("");
            setSelectedRoom("");
            setCheckIn("");
            setCheckOut("");
            setSelectedServices([]);
        } catch (e: any) {
            console.error(e);
            alert("Error creating booking: " + (e.response?.data || e.message));
        }
    };

    return (
        <Card className="max-w-2xl mx-auto">
            <CardHeader>
                <CardTitle>Create New Booking</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="space-y-2">
                    <Label>Guest</Label>
                    <Select onValueChange={setSelectedGuest} value={selectedGuest}>
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
                    <Select onValueChange={setSelectedRoom} value={selectedRoom}>
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
                        <Input type="date" value={checkIn} onChange={e => setCheckIn(e.target.value)} />
                    </div>
                    <div className="space-y-2">
                        <Label>Check-out</Label>
                        <Input type="date" value={checkOut} onChange={e => setCheckOut(e.target.value)} />
                    </div>
                </div>

                <div className="space-y-2">
                    <Label>Services</Label>
                    <div className="flex flex-col gap-2 border p-4 rounded-md">
                        {services.map(s => (
                            <label key={s.id} className="flex items-center gap-2">
                                <input type="checkbox"
                                    checked={selectedServices.includes(s.id.toString())}
                                    onChange={e => {
                                        if (e.target.checked) setSelectedServices([...selectedServices, s.id.toString()]);
                                        else setSelectedServices(selectedServices.filter(id => id !== s.id.toString()));
                                    }}
                                    className="h-4 w-4"
                                />
                                <span>{s.name} (${s.price})</span>
                            </label>
                        ))}
                    </div>
                </div>

                <Button className="w-full" onClick={handleSubmit}>Create Booking</Button>
            </CardContent>
        </Card>
    );
}
