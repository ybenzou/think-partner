<template>
  <div class="h-screen w-screen flex flex-col">
    <div class="p-4 bg-white border-b flex items-center gap-4 shadow z-10">
      <input
        v-model="inputText"
        placeholder="Enter your initial question..."
        class="border px-3 py-2 rounded w-1/2 shadow-sm"
      />
      <button
        @click="submitInitialQuestion"
        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        🌱 Submit Initial Question
      </button>
      <button
        @click="expandSelectedNode"
        class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
        :disabled="!selectedId"
      >
        ➕ Expand Node with AI
      </button>
      <span v-if="selectedId" class="text-gray-600 text-sm">Selected: {{ selectedId }}</span>
    </div>

    <div class="flex-1">
      <VueFlow
        :fit-view-on-init="true"
        class="bg-gray-50"
        @node-click="onNodeClick"
        @pane-click="onPaneClick"
      >
        <Controls />
        <MiniMap />
        <template #node-default="{ id, label, data, selected }">
          <NodeResizer min-width="250" min-height="10" />
          <div
            class="node-default-style"
            :class="[
              // 'rounded border px-2 py-1 text-sm shadow transition-all',
              'break-words whitespace-pre-wrap', // ✅ 内容自动换行
              selected ? 'bg-green-100 border-green-500' : '',
              data.highlighted ? 'ring-2 ring-green-400' : 'bg-white border-gray-200'
            ]"
          >
            {{ label }}
          </div>
        </template>
      </VueFlow>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Controls, MiniMap } from '@vue-flow/additional-components'
import { v4 as uuidv4 } from 'uuid'
import { getLayoutedElements } from './layout.js'
import { NodeResizer } from '@vue-flow/node-resizer'
const { addNodes, addEdges, setNodes, edges } = useVueFlow()

const selectedId = ref(null)
const inputText = ref('')
const allNodes = ref([])

onMounted(() => {
  allNodes.value = []
})

function submitInitialQuestion() {
  if (!inputText.value.trim()) return

  const id = uuidv4().slice(0, 4)
  const newNode = {
    id,
    label: inputText.value,
    position: { x: 0, y: 0 },
    type: 'default',
    data: { highlighted: false },
  }

  allNodes.value = [newNode]
  const { nodes: layouted } = getLayoutedElements(allNodes.value, [])
  allNodes.value = layouted
  setNodes(layouted)
  selectedId.value = id
  inputText.value = ''

  // ✅ 自动触发 LLM 展开
  expandSelectedNode()
}


async function expandSelectedNode() {
  if (!selectedId.value) return

  const parent = allNodes.value.find(n => n.id === selectedId.value)
  if (!parent) return

  const tracePath = []
  function trace(id) {
    const node = allNodes.value.find(n => n.id === id)
    if (!node) return
    tracePath.unshift(node.label)
    const incoming = edges.value.find(e => e.target === id)
    if (incoming) trace(incoming.source)
  }
  trace(parent.id)
  const contextPrompt = tracePath.join(' -> ')

  try {
    console.log("🔁 Sending LLM request...")
    const res = await fetch('/api/llm_expand', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        context: contextPrompt,
        question: parent.label,
      }),
    })

    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const data = await res.json()
    const ideas = data.ideas || []

    console.log("✅ LLM ideas received:", ideas)

    if (ideas.length === 0) {
      alert("LLM returned no ideas. Please try again.")
      return
    }

    const newNodes = []
    const newEdges = []

    for (const idea of ideas) {
      const id = uuidv4().slice(0, 4)
      newNodes.push({
        id,
        label: idea,
        position: { x: 0, y: 0 },
        type: 'default',
        data: { highlighted: false },
      })
      newEdges.push({ id: `${parent.id}-${id}`, source: parent.id, target: id })
    }

    allNodes.value.push(...newNodes)
    const allEdges = [...edges.value, ...newEdges]
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(allNodes.value, allEdges)

    allNodes.value = layoutedNodes
    setNodes(layoutedNodes)
    addEdges(layoutedEdges, { overwrite: true })
  } catch (err) {
    console.error("❌ LLM request failed:", err)
    alert("LLM API call failed. Check backend or console.")
  }
}

function onNodeClick({ node }) {
  selectedId.value = node.id
  highlightPathToNode(node.id)
  setNodes([...allNodes.value])
}

function onPaneClick() {
  selectedId.value = null
  clearHighlights()
  setNodes([...allNodes.value])
}

function clearHighlights() {
  allNodes.value = allNodes.value.map((node) => ({
    ...node,
    data: { ...node.data, highlighted: false },
  }))
  const resetEdges = edges.value.map((edge) => ({
    ...edge,
    style: { stroke: '#999', strokeWidth: 1 },
  }))
  addEdges(resetEdges, { overwrite: true })
}

function highlightPathToNode(targetId) {
  const highlightedNodeIds = new Set()
  const highlightedEdgeIds = new Set()

  function traceBack(currentId) {
    const incoming = edges.value.filter(e => e.target === currentId)
    for (const edge of incoming) {
      highlightedNodeIds.add(edge.source)
      highlightedEdgeIds.add(edge.id)
      traceBack(edge.source)
    }
  }

  highlightedNodeIds.add(targetId)
  traceBack(targetId)

  allNodes.value = allNodes.value.map((node) => ({
    ...node,
    data: {
      ...node.data,
      highlighted: highlightedNodeIds.has(node.id),
    },
  }))

  const updatedEdges = edges.value.map((edge) => ({
    ...edge,
    style: highlightedEdgeIds.has(edge.id)
      ? { stroke: '#22c55e', strokeWidth: 3 }
      : { stroke: '#999', strokeWidth: 1 },
  }))
  addEdges(updatedEdges, { overwrite: true })
}
</script>

<style scoped>
</style>