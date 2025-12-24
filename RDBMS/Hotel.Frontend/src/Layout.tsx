import { Link, Outlet } from "react-router-dom";

export function Layout() {
    return (
        <div className="min-h-screen bg-background text-foreground font-sans antialiased">
            <header className="border-b">
                <div className="container mx-auto p-4 flex gap-6 items-center">
                    <h1 className="font-bold text-xl">Hotel Manager</h1>
                    <nav className="flex gap-4 text-sm font-medium text-muted-foreground">
                        <Link to="/guests" className="hover:text-primary transition-colors">Guests</Link>
                        <Link to="/bookings/new" className="hover:text-primary transition-colors">Book Room</Link>
                        <Link to="/reports" className="hover:text-primary transition-colors">Reports</Link>
                    </nav>
                </div>
            </header>
            <main className="container mx-auto p-4 py-8">
                <Outlet />
            </main>
        </div>
    );
}
