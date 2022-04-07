<!--
@component

Simple wrapper for implementing a Bulma-based selector
-->

<script>

  export let value;
  export let classOptions = "";

</script>

<div class="select {classOptions}">
  <select bind:value={value}>
    <slot></slot>
  </select>
</div>
