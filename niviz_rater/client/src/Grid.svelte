<!-- 
	@component

  Grid component that groups QC objects into rows containing columns

  Properties:
    items: A list of individual item objects containing {id, name, failed}
    groupFunc: a grouping function to dynamically apply on items
-->
<script>
	import Row from './Row.svelte';
	import QcTile from './QcTile.svelte';

  export let items;
  export let groupFunc;

	let rowKeys = [];
	$: rows = groupFunc(items);
	$: rowKeys = [...rows.keys()];

</script>

<div class="block">

	{#each rowKeys as row}

    <Row rowName={row}>
        {#each rows.get(row) as item}
          <QcTile on:message id={item.id} label={item.name} failed={item.failed}/>
        {/each}
    </Row>

	{/each}


</div>

