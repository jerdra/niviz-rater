<script>

	import { onMount } from 'svelte';
	import { getOverview } from './db.js';

	let overview;

	export async function update(){
		overview = await getOverview();
	}
</script>

<main>
{#if overview}
	<div class="tile is-parent">
		<div class="tile is-child box is-primary notification">
			<strong>Scans</strong>: {overview.numberOfEntities}
		</div>
		<div class="tile is-child box is-primary notification">
			<strong>Rows</strong>: {overview.numberOfRows}
		</div>
		<div class="tile is-child box
		{overview.numberOfUnrated > 0 ? "is-warning" : "is-primary"}
		notification">
			<strong>Unrated</strong>: {overview.numberOfUnrated}
		</div>
	</div>
{/if}
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	.title {
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 200;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>
