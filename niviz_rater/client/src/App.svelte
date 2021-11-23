<!--
	Parent component that constructs the Grid view component
	as well as display summary information about the QC process
-->
<script>
	import Fa from 'svelte-fa';
	import { faSave } from '@fortawesome/free-solid-svg-icons';
	import 'bulma/css/bulma.css';
	import 'bulma-switch/dist/css/bulma-switch.min.css';
	import Summary from './Summary.svelte';
	import Grid from './Grid.svelte';
	import Modal from './Modal.svelte';
	import { onMount } from 'svelte';
	import download from 'downloadjs';
	import { fetchEntities, exportCsv, getEntityView, updateRating } from './db.js';
	import { entities, entityWheel, groupSpec } from './store.js';

	// INITIALIZATION LOGIC //
	let summary;
	let selectedEntityId;
	let displayModal = false;
	let skipRated = false;

	onMount(async () => {
		entities.set(await fetchEntities());
		summary.update();
	});

	async function handleEntityMessages(event){
		// Wrapper for handling EntityID
		selectedEntityId = event.detail.id;
		displayModal = true;
	}

	function getNext(id, previous){
		const i = $entityWheel.map(e => e.id).indexOf(id);
		let searchArr = [
			...$entityWheel.slice(i + 1, $entityWheel.length),
			...$entityWheel.slice(0, i)
		]
		if (previous) {
			searchArr = searchArr.reverse();
		}

		// Now filter for any remaining
		const next = searchArr.filter(e => (!skipRated || e.failed == null));

		if (next.length === 0){
			alert("Finished rating!")
			displayModal = false;
		} else {
			selectedEntityId = next[0].id;
		}
	}

	async function handleNext(event){
		displayModal=false;
		entities.updateRating(event.detail.rating);
		getNext(event.detail.rating.id, false);
		displayModal=true;
	}

	async function handlePrevious(event){
		displayModal=false;
		entities.updateRating(event.detail.rating);
		getNext(event.detail.rating.id, true);
		displayModal=true;
	}

	async function handleClose(event){
		console.log(entities);
		entities.updateRating(event.detail.rating);
		displayModal=false;
	}

	async function downloadCsv(){
		const result = await exportCsv();
		download(result, "participants.tsv", "text/plain");
	}

	// Group View Handling
	const selectorMap = [
		{
			name: "Row Name",
			value: (e) => e.rowName,
			selected: true
		},
		{
			name: "Rating Category",
			value: (e) => (e.rating) ? e.rating.name : 'Unrated',
			selected: false
		},
		{
			name: "Pass/Fail",
			value: (e) => {
				if (e.failed == null){
					return "Unrated"
				} else if (e.failed == true) {
					return "Failed"
				} else {
					return "Pass"
				}
			},
			selected: false
		}
	];

</script>

<!-- Header containing setting to skip rated scans -->
<section class="hero is-info mb-5">
	<div class="hero-body">
		<p class="title">Niviz QC</p>
			<Summary bind:this={summary}/>
	</div>
	<div class="container">
		<button class="button is-medium is-rounded is-warning is-outlined"
		  on:click={downloadCsv}>
			<Fa class="mr-3" icon={faSave}/>
			<span>Export CSV</span>
		</button>
	</div>
	<div class="mb-2">
		<div class="select is-pulled-left ml-3">
			<select bind:value={$groupSpec}>
				{#each selectorMap as {name, value, selected} (name)}
					<option {value} {selected}>{name}</option>
				{/each}
		</div>
		<div class="field is-pulled-right mr-3">
			<input id="filterSwitch"
				type="checkbox"
				class="switch is-warning is-outlined is-rounded is-thin"
				bind:checked={skipRated}
			>
		  <label for="filterSwitch">Skip rated</label>
		</div>
	</div>
</section>

<!-- Wrap in a Modal context -->
<Grid on:message={handleEntityMessages}/>

<!-- Queued modals for viewing should update w/skipRated -->
{#if displayModal}
	{#each $entities as e}
		{#if e.id == selectedEntityId}
			{#await getEntityView(e.id) then view}
				<Modal
					on:close={handleClose}
					on:next={handleNext}
					on:previous={handlePrevious}
					entity={view}/>
			{/await}
		{/if}
	{/each}
{/if}


<style>
	:global(html){
		overflow-x: auto;
	}
</style>
