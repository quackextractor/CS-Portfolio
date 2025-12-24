// Append to existing types.ts or overwrite if simpler. I'll append/overwrite.
export enum GuestType {
    Regular = 0,
    VIP = 1,
    Corporate = 2
}

export interface Guest {
    id: number;
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
    dateOfBirth: string;
    isActive: boolean;
    type: GuestType;
    loyaltyPoints: number;
}

export interface Room {
    id: number;
    roomNumber: string;
    roomTypeId: number;
    isClean: boolean;
    lastMaintenance: string | null;
}

export interface RoomType {
    id: number;
    name: string;
    basePrice: number;
    description: string;
}

export interface Booking {
    id: number;
    guestId: number;
    roomId: number;
    checkIn: string;
    checkOut: string;
    totalPrice: number;
    status: number;
    createdAt: string;
}

export interface CreateBookingRequest {
    guestId: number;
    roomId: number;
    checkIn: string;
    checkOut: string;
    serviceIds: number[];
}

export interface Service {
    id: number;
    name: string;
    price: number;
    isActive: boolean;
}

export interface GuestBookingReport {
    bookingId: number;
    firstName: string;
    lastName: string;
    email: string;
    roomNumber: string;
    checkIn: string;
    checkOut: string;
    status: number;
}

export interface RoomAvailabilityReport {
    roomId: number;
    roomNumber: string;
    roomType: string;
    basePrice: number;
}
