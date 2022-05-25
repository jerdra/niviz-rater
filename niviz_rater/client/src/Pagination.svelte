<!--
	@component

	Component that provides pagination capability for the parent
	container

	Implements an on:change dispatch handler
-->

<script>

  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  function changePage(){
    // Bubble up change event
    dispatch('change', currentPage); 
  }

  async function handleClick(){
  }

  // Determine total number of pages
  export let totalItems;

  // Determine number of items per page
  export let pageSize = 1;

  // Determine the current page that we're on
  export let currentPage;

  // Determine the total number of navigation options 
  // Before truncating
  export let maxNavItems = 5;

  let numPages = 0;
  $: numPages = Math.ceil(totalItems / pageSize);
  $: console.log(numPages)


</script>

{#if numPages < maxNavItems}
  {#each Array(numPages + 1) as _, i }
    <button on:click={() => console.log(i)} class="button">{i}</button> 
  {/each}
{/if}


<style>
</style>
