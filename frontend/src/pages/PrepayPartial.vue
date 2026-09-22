<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
import { METHOD_LABELS } from '../labels'

const route = useRoute()
const loans = ref([])
const loanId = ref(null)
const loan = ref(null)
const base = ref(null)
const elapsed = ref(12)
const amount = ref(100000)
const method = ref('shorten_term')
const persist = ref(true)
const out = ref(null)
const err = ref('')

const loadLoans = async () => {
  loans.value = (await getJSON('/api/loans')).items
  const q = Number(route.query.loan)
  loanId.value = loans.value.some(l => l.id === q) ? q : (loans.value[0]?.id ?? null)
}
const loadLoan = async () => {
  out.value = null; err.value = ''
  if (!loanId.value) { loan.value = null; base.value = null; return }
  loan.value = await getJSON(`/api/loans/${loanId.value}`)
  base.value = await postJSON('/api/schedule', {
    principal: loan.value.principal, annual_rate: loan.value.annual_rate,
    months: loan.value.months, loan_id: loan.value.id, persist: false, preview_rows: 1,
  })
}
const run = async () => {
  err.value = ''; out.value = null
  try {
    out.value = await postJSON('/api/prepay', {
      loan_id: loanId.value, elapsed: elapsed.value,
      amount: amount.value, method: method.value, persist: persist.value,
    })
  } catch (e) { err.value = e.message }
}
onMounted(loadLoans)
watch(loanId, loadLoan)
</script>

<template><div class="page"><h1>提前还部分本金</h1>
<label>贷款
  <select v-model.number="loanId">
    <option v-for="l in loans" :key="l.id" :value="l.id">{{ l.name }}</option>
  </select>
</label>
<p v-if="loan">本金 {{ loan.principal }} · 年利率 {{ loan.annual_rate }}% · {{ loan.months }} 期 · 当前月供 <b>{{ base?.monthly_payment }}</b></p>
<label>已过期数 <input type="number" v-model.number="elapsed" min="1" /></label>
<label>提前还金额 <input type="number" v-model.number="amount" min="0" /></label>
<fieldset>
  <label><input type="radio" value="shorten_term" v-model="method" /> {{ METHOD_LABELS.shorten_term }}</label>
  <label><input type="radio" value="reduce_payment" v-model="method" /> {{ METHOD_LABELS.reduce_payment }}</label>
</fieldset>
<label><input type="checkbox" v-model="persist" /> 落库保存</label>
<button @click="run">试算</button>
<p v-if="err" class="err">已拒绝：{{ err }}</p>
<template v-if="out">
  <h2>新旧对照（{{ METHOD_LABELS[out.method] }}）</h2>
  <table>
    <tr><th></th><th>调整前</th><th>调整后</th></tr>
    <tr><td>月供</td><td>{{ out.old_monthly_payment }}</td><td>{{ out.new_monthly_payment }}</td></tr>
    <tr><td>剩余期数</td><td>{{ out.old_remaining_months }}</td><td>{{ out.new_remaining_months }}</td></tr>
  </table>
  <p>提前还前剩余本金 {{ out.balance_before }} · 扣款后剩余本金 {{ out.balance_after }}</p>
  <p>重算后利息合计 {{ out.total_interest }} · 已付利息 {{ out.interest_paid }} · 节省利息 {{ out.interest_saved }}</p>
  <p v-if="out.run_id">已落库 #{{ out.run_id }} <router-link :to="`/history/${out.run_id}`">查看记录</router-link></p>
  <h2>后续预览</h2>
  <table>
    <tr><th>期</th><th>月供</th><th>本金</th><th>利息</th><th>剩余本金</th></tr>
    <tr v-for="r in out.preview" :key="r.period"><td>{{ r.period }}</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td><td>{{ r.balance }}</td></tr>
  </table>
</template>
</div></template>
