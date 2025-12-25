// Append to existing types.ts or overwrite if simpler. I'll append/overwrite.
export const GuestType = {
    Regular: 0,
    VIP: 1,
    Corporate: 2
} as const;

export type GuestType = typeof GuestType[keyof typeof GuestType];

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

id: number;
roomNumber: string;
roomTypeId: number;
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

export interface ServiceUsageStatsReport {
    serviceName: string;
    usageCount: number;
    totalRevenue: number;
}

export interface RevenueByRoomTypeReport {
    roomTypeName: string;
    totalBookings: number;
    totalRevenue: number;
}
