<!--
	Parent component that constructs the Grid view component
	as well as display summary information about the QC process
-->
<script>
	import { onMount } from 'svelte';
	import download from 'downloadjs';

	import Summary from './Summary.svelte';
	import Grid from './Grid.svelte';
	import Modal from './Modal.svelte';
	import { fetchEntities, exportCsv, getEntityView, updateRating } from './db.js';
	import { entities, entityWheel, groupSpec} from './store.js';
  import { groupBy } from './utils.js';
  import { getNext } from './utils/app.js';

	import Fa from 'svelte-fa';
	import { faSave } from '@fortawesome/free-solid-svg-icons';
	import 'bulma/css/bulma.css';
	import 'bulma-switch/dist/css/bulma-switch.min.css';


	// INITIALIZATION LOGIC //
	let summary;
	let selectedEntityId;
	let displayModal = false;
	let skipRated = false;

  // Grid requirement
  let groupFunc = (items) => groupBy(
    $entities.sort( (a, b) =>
      a.columnName - b.columnName
    ),
    $groupSpec
  )

	onMount(async () => {
		entities.set(await fetchEntities());
		summary.update();
	});

	async function handleEntityMessages(event){
		// Wrapper for handling EntityID
		selectedEntityId = event.detail.id;
		displayModal = true;
	}

  function nextModal(id, previous){
    let next = getNext(id, previous, $entityWheel, skipRated);
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
		nextModal(event.detail.rating.id, false);
		displayModal=true;
	}

	async function handlePrevious(event){
		displayModal=false;
		entities.updateRating(event.detail.rating);
		nextModal(event.detail.rating.id, true);
		displayModal=true;
	}

	async function handleClose(event){
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
      </select>
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
<Grid
  on:message={handleEntityMessages}
  items={$entities}
  groupFunc={groupFunc}/>

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
