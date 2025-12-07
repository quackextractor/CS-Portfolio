# Changelog - Frontend Modernization

## [0.1.0] - 2025-12-07

### Added
- **New Web Application**: Initialized Vite + React + TypeScript application in `ChronoLog/web`.
- **UI Framework**: Integrated Tailwind CSS and shadcn-ui components (Card, Button, Select, Badge, Label).
- **Charts**: Implemented `DashboardCharts` and `MessageCharts` using Recharts for data visualization (Latency line chart, Event Counts bar chart).
- **Timeline**: Created `Timeline` component with paginated log viewing, message template interpolation, and server-side filtering support.
- **API Client**: Strongly typed API client (`src/lib/api.ts`) interfacing with the specific ChronoLog Flask endpoints.
- **Theme**: Dark/Light mode support via CSS variables (default system awareness).

### Technical Details
- **State Management**: Local React state for simplicity (KISS).
- **Performance**: Parallel data fetching for dashboard widgets.
- **Verification**: Verified build pass with strict TypeScript configuration.

### Fixed
- **Mobile Layout**: Removed duplicate components and handled responsive layout correctly.
- **Charts Visualization**: Added X/Y axes to all charts, improved tooltips, and ensured data visibility on mobile.
- **Timeline**: Fixed date truncation issue to ensure full timestamp is visible.

