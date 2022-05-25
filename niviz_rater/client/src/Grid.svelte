<!-- 
	@component

  Grid component that groups QC objects into rows containing columns

  Properties:
    rows: Map from rowName -> individual items to QC
-->
<script>
	import Row from './Row.svelte';
	import QcTile from './QcTile.svelte';

  export let rows;


	let rowKeys = [];
	$: rowKeys = [...rows.keys()];

</script>

<div class="block">

	{#each rowKeys as row}
    <Row rowName={row}>
        {#each rows.get(row) as item}
          <QcTile on:message id={item.id} label={item.name} rating={item.rating}/>
        {/each}
    </Row>
	{/each}


</div>

