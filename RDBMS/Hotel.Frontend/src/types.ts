// Types definitions

export interface Guest {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
    dateOfBirth: string;
    isActive: boolean;
}

export interface Room {
    id: number;
    roomNumber: string;
    roomTypeId: number;
}

export interface RoomType {
    id: number;
    name: string;
    basePrice: number;
}

export interface Booking {
    id: number;
    guestId: number;
    roomId: number;
    checkIn: string;
    checkOut: string;
    totalPrice: number;
}

export interface Service {
    id: number;
    name: string;
    price: number;
}

export interface CreateBookingRequest {
    guestId: number;
    roomId: number;
    checkIn: string;
    checkOut: string;
    serviceIds: number[];
}

export interface GuestBookingReport {
    bookingId: number;
    firstName: string;
    lastName: string;
    email: string;
    roomNumber: string;
    checkIn: string;
    checkOut: string;
}

export interface RoomAvailabilityReport {
    roomId: number;
    roomNumber: string;
    roomType: string;
    basePrice: number;
}

export interface RevenueByRoomTypeReport {
    roomTypeName: string;
    totalBookings: number;
    totalRevenue: number;
}
