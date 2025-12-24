import axios from 'axios';
import type { Guest, Room, Booking, CreateBookingRequest, Service } from './types';

const API_URL = 'http://localhost:5106/api';

export const api = {
    guests: {
        getAll: () => axios.get<Guest[]>(`${API_URL}/guests`).then(r => r.data),
        create: (guest: Omit<Guest, 'id'>) => axios.post<Guest>(`${API_URL}/guests`, guest).then(r => r.data),
        delete: (id: number) => axios.delete(`${API_URL}/guests/${id}`),
    },
    rooms: {
        getAll: () => axios.get<Room[]>(`${API_URL}/rooms`).then(r => r.data),
    },
    services: {
        getAll: () => axios.get<Service[]>(`${API_URL}/services`).then(r => r.data),
    },
    bookings: {
        create: (data: CreateBookingRequest) => axios.post<Booking>(`${API_URL}/bookings`, data).then(r => r.data),
        getAll: () => axios.get<Booking[]>(`${API_URL}/bookings`).then(r => r.data),
    },
    reports: {
        guestBookings: () => axios.get<any[]>(`${API_URL}/reports/guest-bookings`).then(r => r.data),
        availability: () => axios.get<any[]>(`${API_URL}/reports/availability`).then(r => r.data),
    }
};

