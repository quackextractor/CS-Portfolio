import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Layout } from "./Layout";
import { GuestList } from "./pages/GuestList";
import { CreateBooking } from "./pages/CreateBooking";
import { Reports } from "./pages/Reports";
import { Import } from "./pages/Import";


function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/guests" replace />} />
          <Route path="/guests" element={<GuestList />} />
          <Route path="/bookings/new" element={<CreateBooking />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/import" element={<Import />} />

        </Route>
      </Routes>
    </BrowserRouter>
  )
}
export default App
