<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, patchJSON, postJSON } from '../api'
const route = useRoute()
const loan = ref(null)
const sch = ref(null)
const newRate = ref(null)
const saved = ref(false)
const load = async () => {
  loan.value = await getJSON(`/api/loans/${route.params.id}`)
  newRate.value = loan.value.annual_rate
  sch.value = await postJSON('/api/schedule', { principal: loan.value.principal, annual_rate: loan.value.annual_rate, months: loan.value.months, loan_id: loan.value.id, persist: false, preview_rows: 6 })
}
const saveRate = async () => {
  saved.value = false
  loan.value = await patchJSON(`/api/loans/${loan.value.id}`, { annual_rate: newRate.value })
  saved.value = true
  await load()
}
onMounted(load); watch(() => route.params.id, load)
</script>
<template><div class="page" v-if="loan"><h1>{{ loan.name }}</h1>
<p>月供 <span class="hero-num">{{ sch?.monthly_payment }}</span></p>
<label>档案年利率% <input v-model.number="newRate" step="0.01" /></label>
<button @click="saveRate">保存利率</button><span v-if="saved"> 已保存</span>
<p><router-link :to="`/prepay?loan=${loan.id}`">提前还款试算 →</router-link></p>
<table><tr v-for="r in sch?.preview" :key="r.period"><td>{{ r.period }}</td><td>{{ r.payment }}</td><td>{{ r.principal }}</td><td>{{ r.interest }}</td></tr></table>
</div></template>
