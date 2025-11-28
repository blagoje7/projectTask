<template>
  <div>
    <h1>Project Task View</h1>
    <p>Role: {{ role }}</p>
  </div>
</template>

<script setup>
const role = localStorage.getItem('role');
</script>
