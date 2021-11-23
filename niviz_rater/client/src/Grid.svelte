<!-- @component

	The Grid component has ownership over Entity components which represent
	a single imaging object that is to be assessed.

	This ownership is carried through by Row components which group
	Entity components into sortable rows


	Properties:
		- rowEntities: List of row entities maintained by Grid
		- filterView: current filter being used
-->
<script>
	import Row from './Row.svelte';
	import { groupSpec, groupedEntities } from './store.js';
	import { groupBy } from './utils.js';

	let rowKeys = [];
	let rows;
	$: rows = $groupedEntities;
	$: rowKeys = [...rows.keys()];

</script>

<div class="block">
	{#each rowKeys as row}
			<Row on:message 
		rowName={row}
		entities={rows.get(row)}/>
	{/each}
</div>

<style>
</style>
