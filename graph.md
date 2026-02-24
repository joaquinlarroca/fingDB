# fingDB Graph Visualization - Technical Documentation

This document provides a detailed explanation of the prerequisite graph visualization in fingDB.

## Overview

The graph visualization is an interactive tool that displays the relationships between courses (materias) at the Faculty of Engineering. It helps students understand:

- **Prerequisites**: Which courses must be completed before taking another course
- **Course dependencies**: How different courses relate to each other
- **Career structure**: Which courses are mandatory vs optional for specific careers
- **Semester planning**: Visual representation of the ideal course sequence

## Technologies Used

| Technology | Purpose |
|------------|---------|
| **Vue.js 3** | Frontend framework for reactive UI components |
| **D3.js v7** | Data visualization library for rendering the graph |
| **SVG** | Scalable Vector Graphics for crisp rendering at any zoom level |

## Graph Structure

### Nodes (Courses)

Each node represents a course (materia) and displays:
- **Course name** (truncated if necessary)
- **Course code** (e.g., "MAT111", "COM111")
- **Credits** (e.g., "9 créd." or "9 créd. (mín: 45)")
- **Period indicator** (colored dot)

### Edges (Prerequisites)

The directed edges represent prerequisite relationships:
- **Direction**: From prerequisite → to course that requires it
- **Visualization**: Curved Bezier paths flowing downward
- **Meaning**: If there's an edge from A to B, then A must be completed before B

## Visual Layout Algorithm

The graph uses a custom layout algorithm designed specifically for academic prerequisite graphs:

### 1. Level Calculation

Each course is assigned a "level" (semester) based on its prerequisites:
- Courses with no prerequisites → Level 0 (first semester)
- Course level = max(level of all prerequisites) + 1

This creates a topological ordering where prerequisite courses appear above courses that require them.

### 2. Grouping by Institute

Courses are grouped by their department (instituto):
- Instituto de Computación
- Instituto de Matemática y Estadística
- Instituto de Ingeniería Eléctrica
- etc.

Each institute forms a vertical column in the visualization.

### 3. Overflow Handling

When more than 4 courses exist at the same level within an institute, they wrap to additional visual rows to prevent overcrowding.

### 4. Conflict Resolution

A final pass ensures all prerequisite edges flow downward:
- If an edge would go upward (target above source), the target is moved to a lower level
- This process repeats until no conflicts exist

## Interactive Features

### Navigation

| Action | Result |
|--------|--------|
| **Scroll wheel** | Zoom in/out |
| **Click + Drag** | Pan the view |
| **Double-click** | Reset view |
| **Home button** | Center and reset zoom |

### Course Interaction

| Action | Result |
|--------|--------|
| **Click on node** | Open detail modal |
| **Hover on node** | Highlight connected prerequisite links |
| **Click in sidebar** | Focus on course in graph |

### Filtering

The sidebar allows filtering by:
- **Career**: Shows only courses in selected career
  - Mandatory courses: White border
  - Optional courses: Yellow border
  - Profile courses: Orange border
- **Profile**: Specialization within a career
- **Search**: Find courses by name
- **Math Initial**: Toggle "Matemática Inicial" prerequisite

## Color Coding

### Period Colors

| Color | Period |
|-------|--------|
| 🔵 Blue | Bisemestral (bimonthly) |
| 🟣 Purple | Par (even semester) |
| 🩷 Pink | Impar (odd semester) |

### Link Colors (on hover)

| Color | Meaning |
|-------|---------|
| 🔴 Red | Incoming: This course requires the hovered course |
| 🟢 Green | Outgoing: The hovered course is a prerequisite for this one |

## Data Flow

```
API Request
    ↓
/materias/all/con-previas
    ↓
JSON Response
    ↓
buildGraphData()
    ↓
Nodes + Links
    ↓
calculateLevels()
    ↓
Position calculation
    ↓
D3.js rendering
    ↓
Interactive SVG
```

## API Endpoints Used

| Endpoint | Data Retrieved |
|----------|---------------|
| `/materias/all/con-previas` | All courses with their prerequisites |
| `/carreras` | List of careers |
| `/perfiles/by-carrera/{id}` | Profiles for a career |
| `/institutos` | List of institutes/departments |

## Code Structure

The visualization is implemented in two main files:

### `graph.html`
- HTML structure with Vue.js templates
- CSS styling (dark theme inspired by GitHub)
- Container div for the graph

### `graph.js`
- **API_CONFIG**: Dynamic API URL detection
- **buildGraphData()**: Transform API data to graph format
- **calculateLevels()**: Compute semester levels
- **renderGraph()**: Main D3.js rendering function
- **highlightLinks()**: Interactive link highlighting
- **focusAndOpenModal()**: Navigate to specific course

## Performance Considerations

- **Lazy rendering**: Graph only renders after data loads
- **SVG vs Canvas**: SVG used for better interactivity and accessibility
- **Efficient updates**: Only re-renders when filters change
- **Debounced search**: Prevents excessive filtering on typing

## Browser Support

The graph works in all modern browsers that support:
- ES6+ JavaScript
- SVG 1.1
- CSS Grid/Flexbox

Tested on:
- Chrome/Edge (Chromium)
- Firefox
- Safari
- Mobile browsers (iOS Safari, Chrome for Android)

## Future Improvements

Potential enhancements could include:
- Path finding: Show the recommended path from one course to another
- Workload visualization: Display semester workload based on credit hours
- Mobile app: Native mobile version
- Offline support: PWA with local data caching

## Contributing

When modifying the graph visualization:

1. **Understand the data flow**: Start with `buildGraphData()` to see how API data becomes graph elements
2. **Test edge cases**: Ensure graph renders correctly with cycles, isolated nodes, and large datasets
3. **Maintain accessibility**: Ensure keyboard navigation and screen reader compatibility
4. **Document changes**: Update this file with any significant architectural changes
