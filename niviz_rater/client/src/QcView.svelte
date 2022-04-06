<!--
  @component

  Interactive QC Interface
-->

<script>

  import Grid from './Grid.svelte';
  import Modal from './Modal.svelte';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  export let skipRated; // whether to skip already rated items
  export let items; // list of items to rate
  export let groupFunc; // function to use in order to group items into rows
  export let retrieveItemFunc; // function used to retrieve item information

  let displayModal = false;
  let selectedItemId;

  $: rows = groupFunc(items);
  $: itemWheel = [...rows.values()]

  function getNext(id, previous=false){
    const i = items.map(e => e.id).indexOf(id);
    let searchArr = [
      ...items.slice(i + 1, items.length),
      ...items.slice(0, i)
    ]
    if (previous) {
      searchArr = searchArr.reverse();
    }

    // Now filter for any remaining
    const next = searchArr.filter(e => (!skipRated || e.failed == null));
    return next
  }

  function nextModal(id, previous=false){
    let next = getNext(id, previous, itemWheel, skipRated);
    if (next.length === 0){
      alert("Finished rating!")
      displayModal = false;
    } else {
      selectedItemId = next[0].id;
    }
  }

  async function sendRating(rating){
    dispatch('rated', rating);
  }

  async function handleItemClick(event){
		selectedItemId = event.detail.id;
		displayModal = true;
	}

	async function handleNext(event){
		displayModal=false;
    sendRating(event.detail.rating);
		nextModal(event.detail.rating.id);
		displayModal=true;
	}

	async function handlePrevious(event){
		displayModal=false;
    sendRating(event.detail.rating);
		nextModal(event.detail.rating.id, true);
		displayModal=true;
	}

	async function handleClose(event){
    sendRating(event.detail.rating);
		displayModal=false;
	}


</script>

<Grid
  on:message={handleItemClick}
  rows={rows}/>

{#if displayModal}
	{#each items as item}
		{#if item.id == selectedItemId}
			{#await retrieveItemFunc(item.id) then view}
				<Modal
					item={view}
          on:close={handleClose}
          on:next={handleNext}
          on:previous={handlePrevious}
          />
			{/await}
		{/if}
	{/each}
{/if}
