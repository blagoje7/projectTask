<template>
  <div class="whiteboard-container">
    <div class="toolbar">
      <button @click="goBack" class="back-btn">Back to Project</button>
      <div class="divider"></div>
      <button @click="setTool('pen')" :class="{ active: currentTool === 'pen' }" title="Pen">
        ✏️ Pen
      </button>
      <button @click="setTool('eraser')" :class="{ active: currentTool === 'eraser' }" title="Eraser">
        🧹 Eraser
      </button>
      <button @click="setTool('note')" :class="{ active: currentTool === 'note' }" title="Sticky Note">
        📝 Sticky Note
      </button>
      <button v-if="canViewHistory" @click="toggleHistory" title="History">
        📜 History
      </button>
      <input type="color" v-model="color" title="Color" class="color-picker" v-if="currentTool === 'pen'">
      <div class="brush-size" v-if="currentTool === 'pen' || currentTool === 'eraser'">
          <label>Size:</label>
          <input type="range" min="1" max="20" v-model.number="lineWidth" title="Brush Size">
      </div>
      <div class="status" :class="{ connected: isConnected }">
        {{ isConnected ? '🟢 Connected' : '🔴 Disconnected' }}
      </div>
    </div>
    
    <div class="canvas-wrapper" ref="canvasWrapper">
      <canvas 
        ref="canvas" 
        class="whiteboard-canvas"
        @mousedown="startDrawing" 
        @mousemove="draw" 
        @mouseup="stopDrawing" 
        @mouseleave="stopDrawing"
      ></canvas>
      
      <!-- Notes Layer -->
      <div 
        v-for="note in notes" 
        :key="note.elementId" 
        class="sticky-note" 
        :style="{ left: note.x + 'px', top: note.y + 'px', backgroundColor: note.color }"
        @mousedown="startDraggingNote($event, note)"
      >
        <div class="note-header">
            <span class="note-author" v-if="note.createdByName">{{ note.createdByName }}</span>
            <button class="delete-btn" @click.stop="deleteNote(note)">×</button>
        </div>
        <textarea 
            v-model="note.text" 
            @change="updateNote(note)" 
            @mousedown.stop
            placeholder="Write here..."
        ></textarea>
      </div>
    </div>
    
    <!-- History Modal -->
    <div v-if="showHistory" class="modal-overlay" @click.self="showHistory = false">
      <div class="modal">
        <h3>Whiteboard History</h3>
        <div class="history-list">
          <div v-for="action in historyLog" :key="action.actionId" class="history-item">
            <div class="history-header">
                <span class="history-user">{{ action.userName }}</span>
                <span class="history-time">{{ new Date(action.timestamp * 1000).toLocaleString() }}</span>
            </div>
            <div class="history-details">
                {{ formatHistoryAction(action) }}
            </div>
            <div v-if="hasPreview(action)" class="history-preview-btn">
               <button @click.stop="togglePreview(action)">{{ action.showPreview ? 'Hide' : 'Show' }} Drawing</button>
            </div>
            <div v-if="action.showPreview" class="history-drawing-preview">
                <svg :viewBox="getSvgViewBox(action)" class="preview-svg">
                   <path :d="getSvgPath(action)" :stroke="getSvgColor(action)" fill="none" :stroke-width="getSvgStrokeWidth(action)" />
                </svg>
            </div>
          </div>
          <div v-if="historyLog.length === 0" class="empty-history">No history found.</div>
        </div>
        <button @click="showHistory = false" class="close-modal-btn">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { io } from 'socket.io-client';
import { API_BASE_URL } from '../utils/api';

const route = useRoute();
const router = useRouter();
const projectId = route.params.id;
const canvas = ref(null);
const canvasWrapper = ref(null);
const ctx = ref(null);
const socket = ref(null);
const isConnected = ref(false);

// State
const currentTool = ref('pen');
const color = ref('#000000');
const lineWidth = ref(2);
const isDrawing = ref(false);
const notes = ref([]);
const showHistory = ref(false);
const historyLog = ref([]);

// User info
import { getUserId, getUserRole, getUsername } from '../utils/auth';

const userId = getUserId();
const userRole = getUserRole();
const canViewHistory = ['admin', 'manager'].includes(userRole);

// Helper for formatting history
function formatHistoryAction(action) {
    // Basic Parsing of Data
    let d = action.data;
    if (typeof d === 'string') {
        try {
            d = JSON.parse(d);
        } catch (e) {}
    }

    // Try to infer type if missing
    let type = action.elementType;
    if (!type || type === 'element') {
        if (d) {
            // Path detection
            if (d.points || (d.after && d.after.points)) {
                type = 'path';
            }
            // Note detection
            else if (d.text !== undefined || (d.after && d.after.text !== undefined)) {
                type = 'note';
            }
            // Old format fallback
            else if (d.content && d.content.points) type = 'path';
            else if (d.content && d.content.text !== undefined) type = 'note';
        }
    }
    
    // Default fallback
    if (!type) type = 'element';

    const actionType = action.actionType || 'unknown';
    
    // Friendly action verb
    let verb = actionType;
    if (actionType === 'add') verb = 'Added';
    if (actionType === 'modify') verb = 'Edited';
    if (actionType === 'delete') verb = 'Deleted';
    
    // Coordinates info
    let locationInfo = '';
    let x, y;
    
    // Extract coordinates based on type and action
    if (type === 'note') {
        // Data structure for note: {x, y, text, ...}
        // For modify: {before: {..}, after: {..}}
        const target = (actionType === 'modify' && d && d.after) ? d.after : d;
        if (target) {
             // Handle nested content case (legacy)
             const src = target.content || target;
             if (src.x !== undefined && src.y !== undefined) {
                 x = Math.round(src.x);
                 y = Math.round(src.y);
                 locationInfo = ` at (${x}, ${y})`;
             }
        }
    } else if (type === 'path') {
        // Data structure for path: {points: [{x,y},...], ...}
        const target = (actionType === 'modify' && d && d.after) ? d.after : d;
        if (target) {
            const src = target.content || target;
            if (src.points && src.points.length > 0) {
                x = Math.round(src.points[0].x);
                y = Math.round(src.points[0].y);
                locationInfo = ` starting at (${x}, ${y})`;
            }
        }
    }

    // Check content for preview
    let textPreview = '';
    
    if (d) {
        if (type === 'note') {
            // For updates, the content is in d.after
            if (actionType === 'modify' && d.after) {
                 const src = d.after.content || d.after;
                 if (src.text) textPreview = src.text;
            } 
            // For add/delete, it's directly in d
            else {
                 const src = d.content || d;
                 if (src.text) textPreview = src.text;
            }
        }
    }
    
    if (type === 'path') {
        return `${verb} a drawing${locationInfo}`;
    } else if (type === 'note') {
        const snippet = textPreview ? `: "${textPreview.substring(0, 20)}${textPreview.length>20?'...':''}"` : '';
        return `${verb} sticky note${locationInfo}${snippet}`;
    }
    
    // Fallback
    return `${verb} ${type} (${action.elementId ? action.elementId.substring(0,8) : ''})${locationInfo}`;
}

// Drawing state
let lastX = 0;
let lastY = 0;
let currentPath = [];

// Dragging notes state
let draggingNote = null;
let dragOffsetX = 0;
let dragOffsetY = 0;

function toggleHistory() {
    showHistory.value = !showHistory.value;
    if (showHistory.value) {
        historyLog.value = []; // clear old
        socket.value.emit('get_history', { projectId, userId });
    }
}

function goBack() {
  router.push(`/projects/${projectId}`);
}

function setTool(tool) {
  currentTool.value = tool;
  if (tool === 'eraser') {
      // Default to larger size for eraser if needed, but let's just stick to current valid width or a larger default
      if (lineWidth.value < 10) lineWidth.value = 10;
  }
}

function initCanvas() {
  const c = canvas.value;
  const wrapper = canvasWrapper.value;
  if (!c || !wrapper) return;
  c.width = wrapper.clientWidth;
  c.height = wrapper.clientHeight;
  ctx.value = c.getContext('2d');
  ctx.value.lineCap = 'round';
  ctx.value.lineJoin = 'round';
  
  window.addEventListener('resize', resizeCanvas);
}

function resizeCanvas() {
    // Ideally redraw here
}

function initSocket() {
  socket.value = io(API_BASE_URL);
  
  socket.value.on('connect', () => {
    isConnected.value = true;
    socket.value.emit('join_project', { projectId, userId });
  });
  
  socket.value.on('disconnect', () => {
    isConnected.value = false;
  });

  socket.value.on('init_whiteboard', (elements) => {
    const c = canvas.value;
    if(ctx.value) ctx.value.clearRect(0, 0, c.width, c.height);
    notes.value = [];
    
    elements.forEach(el => {
      // NoSQL backend sends 'content' as a real object now.
      // We handle both cases just in case (e.g. legacy data or robust code)
      let content = el.content;
      if (typeof content === 'string') {
          try {
             content = JSON.parse(content);
          } catch (e) { console.error('Error parsing content', e); return; }
      }

      if (el.type === 'path') {
        drawPath(content);
      } else if (el.type === 'note') {
        notes.value.push({ ...content, elementId: el.elementId, createdByName: el.createdByName });
      }
    });
  });

  socket.value.on('drawing', (data) => {
    drawFromServer(data);
  });
  
  socket.value.on('element_saved', (el) => {
      let content = el.content;
      if (typeof content === 'string') {
          try { content = JSON.parse(content); } catch (e) {}
      }

      if (el.type === 'note') {
          const tempId = content.tempId;
          
          const existingIdx = notes.value.findIndex(n => n.elementId === tempId || n.elementId === el.elementId);
          if (existingIdx !== -1) {
                // Replace temp note with real note from server
                notes.value[existingIdx] = { ...content, elementId: el.elementId, createdByName: el.createdByName };
          } else {
                notes.value.push({ ...content, elementId: el.elementId, createdByName: el.createdByName });
          }
      } else if (el.type === 'path') {
          // Path already drawn via 'drawing' event or local interaction
      }
  });
  
  socket.value.on('element_updated', (el) => {
      if (el.type === 'note') {
          let content = el.content;
          if (typeof content === 'string') {
               try { content = JSON.parse(content); } catch(e) {}
          }

          const idx = notes.value.findIndex(n => n.elementId === el.elementId);
          if (idx !== -1) {
              // update in place
              notes.value[idx] = { ...notes.value[idx], ...content };
          }
      }
  });

  socket.value.on('element_deleted', (data) => {
      notes.value = notes.value.filter(n => n.elementId !== data.elementId);
  });
  
  socket.value.on('history_data', (data) => {
      historyLog.value = data;
  });
  
  socket.value.on('error', (err) => {
      alert(err.message);
  });
}

function hasPreview(action) {
    // Only show preview for paths (drawings)
    let type = action.elementType;
    let d = action.data;
    if (typeof d === 'string') { try { d = JSON.parse(d); } catch(e) {} }
    
    // Infer type if needed (reusing logic from formatHistoryAction mostly)
    if (!type || type === 'element') {
        if (d) {
            if (d.points || (d.after && d.after.points) || (d.content && d.content.points)) type = 'path';
        }
    }
    
    return type === 'path';
}

function togglePreview(action) {
    action.showPreview = !action.showPreview;
}

function getPathData(action) {
    let d = action.data;
    if (typeof d === 'string') { try { d = JSON.parse(d); } catch(e) {} }
    
    const actionType = action.actionType || 'unknown';
    
    // Target object containing points
    // modify -> d.after, other -> d
    // then check .content or direct
    let target = (actionType === 'modify' && d && d.after) ? d.after : d;
    
    if (target) {
        if (target.points) return target; // direct points
        if (target.content && target.content.points) return target.content; // nested content
    }
    return null;
}

function getSvgPath(action) {
    const data = getPathData(action);
    if (!data || !data.points || data.points.length < 2) return '';
    
    // Simplification for preview
    const pts = data.points;
    let path = `M ${pts[0].x} ${pts[0].y}`;
    // reduce points for smoother preview if massive
    const step = Math.max(1, Math.floor(pts.length / 50));
    for(let i=1; i<pts.length; i+=step) {
        path += ` L ${pts[i].x} ${pts[i].y}`;
    }
    return path;
}

function getSvgColor(action) {
    const data = getPathData(action);
    if (data && data.color) {
        // If it's an eraser stroke (white), show as gray in preview so it's visible
        if (data.color.toUpperCase() === '#FFFFFF' || data.color.toUpperCase() === '#FFF') return '#E0E0E0';
        return data.color;
    }
    return '#000000';
}

function getSvgStrokeWidth(action) {
     const data = getPathData(action);
     return (data && data.width) ? data.width : 2;
}

function getSvgViewBox(action) {
    const data = getPathData(action);
    if (!data || !data.points || data.points.length === 0) return '0 0 100 100';
    
    const pts = data.points;
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    
    pts.forEach(p => {
        if (p.x < minX) minX = p.x;
        if (p.y < minY) minY = p.y;
        if (p.x > maxX) maxX = p.x;
        if (p.y > maxY) maxY = p.y;
    });
    
    // Add padding
    const padding = 10;
    minX -= padding;
    minY -= padding;
    const width = (maxX - minX) + (padding * 2);
    const height = (maxY - minY) + (padding * 2);
    
    return `${minX} ${minY} ${width} ${height}`;
}

// Drawing Logic
function startDrawing(e) {
  if (currentTool.value !== 'pen' && currentTool.value !== 'eraser') {
      if (currentTool.value === 'note') {
          createNote(e);
      }
      return;
  }
  isDrawing.value = true;
  const { x, y } = getPos(e);
  lastX = x;
  lastY = y;
  currentPath = [{ x, y }];
}

function draw(e) {
  if (!isDrawing.value) return;
  const { x, y } = getPos(e);
  
  const drawColor = currentTool.value === 'eraser' ? '#FFFFFF' : color.value;
  drawSegment(lastX, lastY, x, y, drawColor, lineWidth.value);
  
  socket.value.emit('draw', {
    projectId,
    x0: lastX,
    y0: lastY,
    x1: x,
    y1: y,
    color: drawColor,
    width: lineWidth.value
  });
  
  currentPath.push({ x, y });
  lastX = x;
  lastY = y;
}

function stopDrawing() {
  if (!isDrawing.value) return;
  isDrawing.value = false;
  
  if (currentPath.length > 1) {
      const drawColor = currentTool.value === 'eraser' ? '#FFFFFF' : color.value;
      socket.value.emit('save_element', {
          projectId,
          userId,
          type: 'path',
          content: { points: currentPath, color: drawColor, width: lineWidth.value }
      });
  }
  currentPath = [];
}

function drawSegment(x0, y0, x1, y1, colorStr, width = 2) {
    if (!ctx.value) return;
    ctx.value.beginPath();
    ctx.value.moveTo(x0, y0);
    ctx.value.lineTo(x1, y1);
    ctx.value.strokeStyle = colorStr;
    ctx.value.lineWidth = width;
    ctx.value.stroke();
    ctx.value.closePath();
}

function drawFromServer(data) {
    drawSegment(data.x0, data.y0, data.x1, data.y1, data.color, data.width || 2);
}

function drawPath(content) {
    const points = content.points;
    const c = content.color;
    const w = content.width || 2;
    if (!points || points.length < 2) return;
    
    ctx.value.beginPath();
    ctx.value.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) {
        ctx.value.lineTo(points[i].x, points[i].y);
    }
    ctx.value.strokeStyle = c;
    ctx.value.lineWidth = w;
    ctx.value.stroke();
    ctx.value.closePath();
}

function getPos(e) {
    const rect = canvas.value.getBoundingClientRect();
    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
    };
}

// Note Logic

function createNote(e) {
    const { x, y } = getPos(e);
    // Temp ID
    const tempId = 'temp-' + Date.now();
    const note = {
        elementId: tempId,
        x,
        y,
        text: '',
        color: '#fff740', // default yellow
        createdByName: getUsername() || 'Me'
    };
    notes.value.push(note);
    saveNote(note);
}

function saveNote(note) {
    socket.value.emit('save_element', {
        projectId,
        userId,
        type: 'note',
        content: {
            tempId: note.elementId, // Send temp ID to link back
            x: note.x,
            y: note.y,
            text: note.text,
            color: note.color
        }
    });
}

function updateNote(note) {
    if (String(note.elementId).startsWith('temp-')) return;
    
    socket.value.emit('update_element', {
        projectId,
        userId,
        elementId: note.elementId,
        content: {
            x: note.x,
            y: note.y,
            text: note.text,
            color: note.color
        }
    });
}

function deleteNote(note) {
    if (confirm('Delete this note?')) {
        if (!String(note.elementId).startsWith('temp-')) {
             socket.value.emit('delete_element', {
                projectId,
                userId,
                elementId: note.elementId
            });
        }
        notes.value = notes.value.filter(n => n.elementId !== note.elementId);
    }
}

function startDraggingNote(e, note) {
    if (e.target.tagName.toLowerCase() === 'textarea') return;
    if (e.target.tagName.toLowerCase() === 'button') return; 

    draggingNote = note;
    const rect = canvasWrapper.value.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    dragOffsetX = mouseX - note.x;
    dragOffsetY = mouseY - note.y;
    
    window.addEventListener('mousemove', onDragNote);
    window.addEventListener('mouseup', stopDragNote);
}

function onDragNote(e) {
    if (!draggingNote) return;
    const rect = canvasWrapper.value.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    draggingNote.x = mouseX - dragOffsetX;
    draggingNote.y = mouseY - dragOffsetY;
}

function stopDragNote() {
    if (draggingNote) {
        updateNote(draggingNote);
        draggingNote = null;
    }
    window.removeEventListener('mousemove', onDragNote);
    window.removeEventListener('mouseup', stopDragNote);
}

onMounted(() => {
    initCanvas();
    initSocket();
});

onUnmounted(() => {
    if (socket.value) socket.value.disconnect();
    window.removeEventListener('resize', resizeCanvas);
    window.removeEventListener('mousemove', onDragNote);
    window.removeEventListener('mouseup', stopDragNote);
});
</script>

<style scoped>
.whiteboard-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  background: #f0f0f0;
}
.toolbar {
  padding: 10px;
  background: white;
  display: flex;
  gap: 10px;
  align-items: center;
  border-bottom: 1px solid #ccc;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.active {
    background-color: #007bff;
    color: white;
    border-color: #0056b3;
}
.divider {
    width: 1px;
    height: 20px;
    background: #ccc;
}
.canvas-wrapper {
    flex: 1;
    position: relative;
    overflow: hidden;
    cursor: crosshair;
}
.whiteboard-canvas {
    display: block;
    background: white;
}

.history-preview-btn button {
    margin-top: 5px;
    font-size: 0.8rem;
    padding: 2px 8px;
    cursor: pointer;
}

.history-drawing-preview {
    margin-top: 10px;
    border: 1px solid #ddd;
    background: #f9f9f9;
    padding: 5px;
    border-radius: 4px;
    text-align: center;
}

.preview-svg {
    max-width: 100%;
    max-height: 150px;
    border: 1px dashed #ccc;
    background: white;
}

.brush-size {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.9rem;
}
.brush-size input {
    width: 60px;
}

.sticky-note {
    position: absolute;
    width: 200px;
    min-height: 150px;
    padding: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    display: flex;
    flex-direction: column;
    cursor: grab;
    border-radius: 2px;
}
.sticky-note:active {
    cursor: grabbing;
}
.sticky-note textarea {
    flex: 1;
    background: transparent;
    border: none;
    resize: none;
    width: 100%;
    outline: none;
    font-family: 'Comic Sans MS', cursive, sans-serif;
    font-size: 14px;
}
.note-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
    font-size: 0.8em;
    color: #555;
    cursor: grab;
    user-select: none;
}
.delete-btn {
    background: none;
    border: none;
    color: #888;
    cursor: pointer;
    font-weight: bold;
    font-size: 16px;
    line-height: 1;
}
.delete-btn:hover {
    color: red;
}
.status {
    margin-left: auto;
    font-size: 0.8em;
    font-weight: bold;
}
.status.connected {
    color: green;
}
.back-btn {
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px 10px;
    cursor: pointer;
}
.back-btn:hover {

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}
.modal {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 500px;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
}
.history-list {
    flex: 1;
    overflow-y: auto;
    margin: 10px 0;
    border: 1px solid #eee;
}
.history-item {
    padding: 10px;
    border-bottom: 1px solid #eee;
}
.history-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.9em;
    font-weight: bold;
    margin-bottom: 5px;
}
.history-time {
    color: #888;
    font-size: 0.8em;
}
.close-modal-btn {
    align-self: flex-end;
    background: #007bff;
    color: white;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
}
    background: #e2e6ea;
}
button {
    padding: 5px 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
    cursor: pointer;
}
.color-picker {
    width: 40px;
    height: 30px;
    padding: 0;
    border: none;
    cursor: pointer;
}
</style>
