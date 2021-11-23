<!--
	@component

	Component representing a stack of Modals for the user to traverse through
	Wraps a Modal component to allow for traversal across modals without saving and closing

	Functionality:

	1. Should keep track of current set of rated or un-rated scans - depending on user preference
	2. Current modal should be standard view, next modal should load in the background?
	3. Use positioning transitions/tweening to handle switching between modals
	4. Destruct the previous modal

	# Start with this then build to above depending on whether it runs efficiently
	5. Alternatively should just change the info view to update without closing/transitioning modal
-->
<script>

	import Modal from './Modal.svelte';

	export let ratingStack = [];
	let currentIndex = 0;

	$: console.log(ratingStack);

</script>

{#each ratingStack as item, i}
	{#if i == currentIndex}
		{console.log(item)}
	{/if}
{/each}

