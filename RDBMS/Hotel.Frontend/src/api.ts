import axios from 'axios';
import type { Guest, Room, Booking, CreateBookingRequest, BookingService } from './types';

const API_URL = 'http://localhost:5106/api';

export const api = {
    guests: {
        getAll: () => axios.get<Guest[]>(`${API_URL}/guests`).then(r => r.data),
        create: (guest: Omit<Guest, 'id'>) => axios.post<Guest>(`${API_URL}/guests`, guest).then(r => r.data),
        update: (id: number, guest: Guest) => axios.put(`${API_URL}/guests/${id}`, guest).then(r => r.data),
        delete: (id: number) => axios.delete(`${API_URL}/guests/${id}`),
    },
    rooms: {
        getAll: () => axios.get<Room[]>(`${API_URL}/rooms`).then(r => r.data),
        create: (room: Omit<Room, 'id' | 'lastMaintenance'>) => axios.post<Room>(`${API_URL}/rooms`, room).then(r => r.data),
        delete: (id: number) => axios.delete(`${API_URL}/rooms/${id}`),
    },

    bookings: {
        create: (data: CreateBookingRequest) => axios.post<Booking>(`${API_URL}/bookings`, data).then(r => r.data),
        getAll: () => axios.get<Booking[]>(`${API_URL}/bookings`).then(r => r.data),
        get: (id: number) => axios.get<{ booking: Booking; services: BookingService[] }>(`${API_URL}/bookings/${id}`).then(r => r.data),
        delete: (id: number) => axios.delete(`${API_URL}/bookings/${id}`),
    },
    services: {
        getAll: () => axios.get<{ id: number; name: string; price: number }[]>(`${API_URL}/services`).then(r => r.data),
    },
    reports: {
        guestBookings: () => axios.get<any[]>(`${API_URL}/reports/guest-bookings`).then(r => r.data),
        availability: () => axios.get<any[]>(`${API_URL}/reports/availability`).then(r => r.data),

        revenueByRoomType: () => axios.get<any[]>(`${API_URL}/reports/revenue-by-room-type`).then(r => r.data),
    },
    import: {
        guests: (formData: FormData) => axios.post(`${API_URL}/import/guests`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        }).then(r => r.data),
        rooms: (formData: FormData) => axios.post(`${API_URL}/import/rooms`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        }).then(r => r.data),
    }
};

