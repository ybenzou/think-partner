import dagre from 'dagre'

export function getLayoutedElements(nodes, edges) {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))

  dagreGraph.setGraph({
    rankdir: 'TB',     // ⬅️ 如果你希望从左到右，可改为 'TB' 为上下结构
    nodesep: 120,      // 横向节点间距（更宽）
    ranksep: 100,      // 纵向节点间距
  })

  nodes.forEach((node) => {
    const textLength = node.label.length
    const avgCharsPerLine = 60            // ✅ 放大一行的字符容纳量
    const lines = Math.ceil(textLength / avgCharsPerLine)
    const width = 360                     // ✅ 放大宽度，配合 App.vue 的 max-width: 360px
    const height = 40 + lines * 24        // 每行约24px高度

    dagreGraph.setNode(node.id, { width, height })
  })

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  dagre.layout(dagreGraph)

  const layoutedNodes = nodes.map((node) => {
    const pos = dagreGraph.node(node.id)
    return {
      ...node,
      position: {
        x: pos.x - (pos.width ?? 180) / 2,
        y: pos.y - (pos.height ?? 50) / 2,
      },
    }
  })

  return { nodes: layoutedNodes, edges }
}
