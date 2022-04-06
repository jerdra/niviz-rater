<!-- 
	@component

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
	import QcTile from './QcTile.svelte';

	export let displayEntities = new Map();

	let rowKeys = [];
	let rows;
	$: rows = displayEntities;
	$: rowKeys = [...rows.keys()];

</script>

<div class="block">


	{#each rowKeys as row}

    <Row rowName={row}>
        {#each rows.get(row) as entity}
          <QcTile on:message id={entity.id} label={entity.name} failed={entity.failed}/>
        {/each}
    </Row>

	{/each}


</div>

