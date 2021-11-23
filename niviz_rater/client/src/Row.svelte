<!--
	@component

	Filterable Row component contains Entity components allowing
	users to examine rows containing failed QC, incomplete QC or passed QC

	Properties:
		- entities: List of ordered entities stored 
		- orderSpec: Order specification for how to list entities
-->

<script>
	import Entity from './Entity.svelte';

	export let rowName, entities;

	// Should construct key-value mapping of columns to entities
	let columnEntityMap;
	$: columnEntityMap = entities.reduce((m, e) => m.set(e.columnName, e), new Map())

</script>

<!-- Row container -->
	<!-- This is a container that should contain another container -->
<div class="block notification is-primary m-5">
	<div class="columns is-multiline">
		<div class="column notification is-warning is-12">
			<strong>{rowName}</strong>
		</div>
		{#each entities as e}
			<Entity on:message entity={e}/>
		{/each}
	</div>
</div>

<style>
	.notification:not(:last-child){
		margin-bottom: 0;
	}
</style>
