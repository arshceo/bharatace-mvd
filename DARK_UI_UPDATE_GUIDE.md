# BharatAce Dashboard - Dark Glassmorphism UI Update

## Design System

### Color Palette
- **Background**: `#0b1020` → `#0b0f25` → `#101225` (gradient)
- **Card Background**: `radial-gradient from-slate-200/10 to-slate-800/0`
- **Borders**: `border-white/10`
- **Text**: `text-white` for headings, `text-white/60` for secondary
- **Accents**: Violet `#8b5cf6`, Fuchsia `#d946ef`, Indigo `#6366f1`

### Typography
- **Font**: Inter (300, 400, 500, 600, 700)
- **Headings**: `text-[18px] font-semibold tracking-tight`
- **Body**: `text-sm text-white/70`
- **Numbers**: `text-2xl font-semibold tracking-tight`

### Card Style Template
```tsx
<div className="rounded-2xl border border-white/10 bg-[radial-gradient(circle_at_top_left,var(--tw-gradient-stops))] from-slate-200/10 to-slate-800/0 p-6 shadow-xl shadow-black/20">
  {/* Card content */}
</div>
```

## Updated Components

### 1. Dashboard Page (`page.tsx`)
✅ **DONE** - Updated with:
- Dark gradient background
- Background glow effects
- Glassmorphism header
- New color scheme

### 2. Global Styles (`globals.css`)
✅ **DONE** - Added:
- Inter font import
- Dark theme CSS variables
- Font-family declarations

### 3. Components to Update

All components need the base card style:
```tsx
className="rounded-2xl border border-white/10 bg-[radial-gradient(circle_at_top_left,var(--tw-gradient-stops))] from-slate-200/10 to-slate-800/0 p-6 shadow-xl shadow-black/20"
```

#### AttendanceCard.tsx
```tsx
// Loading state
<div className="rounded-2xl border border-white/10 bg-[radial-gradient(circle_at_top_left,var(--tw-gradient-stops))] from-slate-200/10 to-slate-800/0 p-6 shadow-xl shadow-black/20 animate-pulse">
  <div className="h-6 bg-white/10 rounded w-1/2 mb-4"></div>
  <div className="h-20 bg-white/10 rounded"></div>
</div>

// Header
<h3 className="text-[18px] font-semibold text-white tracking-tight">
  Attendance
</h3>
<p className="text-xs text-white/60">Current semester</p>

// Percentage display
<span className="text-2xl font-bold tracking-tight text-emerald-400">
  {attendance.percentage.toFixed(1)}%
</span>

// Progress bar
<div className="h-3 w-full rounded-full bg-white/10 overflow-hidden">
  <div className="h-full bg-gradient-to-r from-emerald-500 to-green-600"></div>
</div>

// Stats boxes
<div className="rounded-lg bg-white/5 border border-white/10 p-3">
  <div className="text-2xl font-semibold text-white tracking-tight">{value}</div>
  <div className="text-xs text-white/60 mt-1">{label}</div>
</div>
```

#### FeeStatusCard.tsx
```tsx
// Icon color: text-fuchsia-400
// Amount display: text-2xl font-semibold tracking-tight text-white
// Status badges:
  - Paid: bg-emerald-500/20 text-emerald-400
  - Pending: bg-yellow-500/20 text-yellow-400
  - Overdue: bg-red-500/20 text-red-400

// Progress bar
<div className="h-2 rounded-full bg-white/10">
  <div className="h-full rounded-full bg-gradient-to-r from-fuchsia-500 to-pink-500"></div>
</div>
```

#### TodayScheduleCard.tsx
```tsx
// Class items
<div className="rounded-lg bg-white/5 border border-white/10 p-3 hover:bg-white/10 transition-all">
  <div className="flex items-center justify-between">
    <div>
      <p className="text-sm font-medium text-white">{subject}</p>
      <p className="text-xs text-white/60">{time}</p>
    </div>
    <span className="px-2 py-1 rounded bg-violet-500/20 text-violet-400 text-xs font-medium">
      {room}
    </span>
  </div>
</div>

// Empty state
<div className="text-center py-8">
  <svg className="h-16 w-16 mx-auto text-white/20 mb-3" />
  <p className="text-white/50">No classes today</p>
</div>
```

#### LibraryCard.tsx
```tsx
// Book items
<div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-white/10">
  <div className="h-12 w-9 rounded bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center">
    <svg className="h-5 w-5 text-white" />
  </div>
  <div className="flex-1">
    <p className="text-sm font-medium text-white">{title}</p>
    <p className="text-xs text-white/60">Due: {date}</p>
  </div>
</div>
```

#### ChatInterface.tsx
```tsx
// Container
<div className="sticky top-20 rounded-2xl border border-white/10 bg-[radial-gradient(circle_at_top_left,var(--tw-gradient-stops))] from-slate-200/10 to-slate-800/0 shadow-xl shadow-black/20 overflow-hidden flex flex-col h-[600px]">

// Header
<div className="p-4 border-b border-white/10">
  <h3 className="text-[18px] font-semibold text-white tracking-tight">
    AI Assistant
  </h3>
</div>

// Messages
<div className="p-3 rounded-lg bg-white/5 border border-white/10">
  <p className="text-sm text-white/90">{message}</p>
</div>

// Input
<input className="flex-1 bg-transparent text-white placeholder:text-white/40 text-sm outline-none" />

// Button
<button className="px-4 py-2 rounded-lg bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white font-medium hover:shadow-lg transition-all">
  Send
</button>
```

#### MyEventsCard.tsx
```tsx
// Event cards
<div className="p-4 border-l-4 border-violet-500 rounded-lg bg-white/5 hover:bg-white/10 transition-all">
  <div className="flex items-center gap-2">
    <span className="px-2 py-1 text-xs font-semibold rounded bg-violet-500/20 text-violet-400">
      {type}
    </span>
  </div>
  <h4 className="font-semibold text-white mt-2">{title}</h4>
  <p className="text-sm text-white/60">{description}</p>
</div>

// Badge
<span className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs font-semibold rounded-full">
  {count} Registered
</span>
```

#### UpcomingEventsCard.tsx
```tsx
// Event type badges
const eventTypeColors = {
  workshop: 'bg-purple-500/20 text-purple-400',
  seminar: 'bg-blue-500/20 text-blue-400',
  competition: 'bg-green-500/20 text-green-400',
  cultural: 'bg-pink-500/20 text-pink-400',
  sports: 'bg-orange-500/20 text-orange-400',
}
```

#### WelcomeCard.tsx
```tsx
<div className="rounded-2xl border border-white/10 bg-[radial-gradient(circle_at_top_left,var(--tw-gradient-stops))] from-slate-200/10 to-slate-800/0 p-6 shadow-xl shadow-black/20">
  <h2 className="text-2xl font-bold text-white tracking-tight">
    Welcome back, {name}!
  </h2>
  <p className="text-white/60 mt-2">
    Here's your academic overview for today
  </p>
</div>
```

## Color Reference

### Status Colors
- **Success/Good**: `text-emerald-400`, `bg-emerald-500/20`
- **Warning**: `text-yellow-400`, `bg-yellow-500/20`
- **Error/Critical**: `text-red-400`, `bg-red-500/20`
- **Info**: `text-sky-400`, `bg-sky-500/20`

### Gradient Combinations
- **Primary**: `from-violet-600 to-fuchsia-600`
- **Success**: `from-emerald-500 to-green-600`
- **Warning**: `from-yellow-500 to-orange-500`
- **Error**: `from-red-500 to-pink-600`
- **Info**: `from-sky-400 to-violet-500`

## Implementation Checklist

- [x] Dashboard page layout
- [x] Global styles with Inter font
- [ ] AttendanceCard
- [ ] FeeStatusCard
- [ ] TodayScheduleCard
- [ ] LibraryCard
- [ ] ChatInterface
- [ ] MyEventsCard
- [ ] UpcomingEventsCard
- [ ] WelcomeCard

## Testing

After implementing, test:
1. Dark theme visibility
2. Hover effects on cards
3. Loading states (skeleton loaders)
4. Empty states
5. Responsive design (mobile, tablet, desktop)
6. Glassmorphism effects
7. Font rendering (Inter)
8. Color contrast (accessibility)

## Notes

- All cards use same base style for consistency
- Maintain glassmorphism effect with `backdrop-blur-lg`
- Use `shadow-xl shadow-black/20` for depth
- Keep `hover:shadow-black/40` for interaction feedback
- Use `transition-all` for smooth animations
- Preserve all existing functionality
- Only update visual styling, not logic

