import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./Layout";
import { GuestList } from "./pages/GuestList";
import { CreateBooking } from "./pages/CreateBooking";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/guests" replace />} />
          <Route path="/guests" element={<GuestList />} />
          <Route path="/bookings/new" element={<CreateBooking />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
export default App
