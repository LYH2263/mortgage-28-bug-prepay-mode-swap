<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON } from '../api'
import { METHOD_LABELS } from '../labels'

const route = useRoute()
const rec = ref(null)
const err = ref('')
const load = async () => {
  err.value = ''; rec.value = null
  try { rec.value = await getJSON(`/api/history/${route.params.id}`) }
  catch (e) { err.value = e.message }
}
onMounted(load)
watch(() => route.params.id, load)
</script>

<template><div class="page"><h1>试算记录 #{{ route.params.id }}</h1>
<p v-if="err" class="err">{{ err }}</p>
<template v-if="rec">
  <p>类型 {{ rec.kind }} · 贷款 #{{ rec.loan_id ?? '—' }} · 写入于 {{ rec.created_at }}</p>
  <h2>写入时输入</h2>
  <table>
    <tr v-for="(v, k) in rec.input" :key="k"><td>{{ k }}</td><td>{{ k === 'method' ? (METHOD_LABELS[v] ?? v) : v }}</td></tr>
  </table>
  <template v-if="rec.kind === 'prepay_partial'">
    <h2>重算结果（{{ METHOD_LABELS[rec.result.method] ?? rec.result.method }}）</h2>
    <table>
      <tr><td>提前还前剩余本金</td><td>{{ rec.result.balance_before }}</td></tr>
      <tr><td>扣款后剩余本金</td><td>{{ rec.result.balance_after }}</td></tr>
      <tr><td>月供</td><td>{{ rec.result.old_monthly_payment }} → {{ rec.result.new_monthly_payment }}</td></tr>
      <tr><td>剩余期数</td><td>{{ rec.result.old_remaining_months }} → {{ rec.result.new_remaining_months }}</td></tr>
      <tr><td>重算后利息合计</td><td>{{ rec.result.total_interest }}</td></tr>
      <tr><td>已付利息</td><td>{{ rec.result.interest_paid }}</td></tr>
      <tr><td>节省利息</td><td>{{ rec.result.interest_saved }}</td></tr>
    </table>
    <h2>后续预览</h2>
    <table>
      <tr><th>期</th><th>月供</th><th>本金</th><th>利息</th><th>剩余本金</th></tr>
      <tr v-for="r in rec.result.preview" :key="r.period"><td>{{ r.period }}</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td></tr>
    </table>
  </template>
  <template v-else>
    <h2>结果</h2>
    <pre>{{ rec.result }}</pre>
  </template>
</template>
</div></template>
