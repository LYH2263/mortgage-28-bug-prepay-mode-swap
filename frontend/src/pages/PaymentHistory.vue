<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
import { METHOD_LABELS } from '../labels'
const items = ref([])
const methodOf = (h) => {
  try { return METHOD_LABELS[JSON.parse(h.input_json).method] ?? '—' } catch { return '—' }
}
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template><div class="page"><h1>试算记录</h1>
<table>
  <tr><th>#</th><th>类型</th><th>处理方式</th><th>时间</th><th></th></tr>
  <tr v-for="h in items" :key="h.id">
    <td>#{{ h.id }}</td><td>{{ h.kind }}</td><td>{{ methodOf(h) }}</td><td>{{ h.created_at }}</td>
    <td><router-link :to="`/history/${h.id}`">打开</router-link></td>
  </tr>
</table>
</div></template>
