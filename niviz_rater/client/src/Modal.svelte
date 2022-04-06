<!--
	@component

	Modal for displaying primary QC interface for interacting
	with and updating QC ratings
-->

<script>
	import { onMount, createEventDispatcher } from 'svelte';
	import { fly, slide, fade } from 'svelte/transition';
	import ItemRatingView from './ItemRatingView.svelte';
	export let item;
	const dispatch = createEventDispatcher();
	let itemRating = {};
	let originalRating = {};
	let modalData;

	// Initialize itemRating
	itemRating.failed = item.failed;
	itemRating.comment = item.comment;
	itemRating.id = item.id
	if (item.rating == null){
		itemRating.rating = null
	} else {
		itemRating.rating = item.rating.id;
	}
	originalRating = Object.assign(originalRating, itemRating);

	const isSame = (a,b) => {
		return(
		Object.entries(a)
			.every(([k, v]) => b[k] == v)
		)
	}

	// Functions to deal with messaging logic
	$: msg = { rating: itemRating }
	const handleClose = () => {
		let result = true;
		const changed = !isSame(originalRating, itemRating);
		if (changed){
			result = window.confirm("Do you want to save changes?");
		}
		if (result) {
			dispatch('close',msg);
		} else {
			dispatch('close', { rating: originalRating });
		}
	}
	const handleNext = () => dispatch('next',msg);
	const handlePrevious = () => dispatch('previous',msg);

	// EventListener setups
	function handleKeydown(event){
		const key = event.key;
		const keyCode = event.keyCode;
		if (!modalData.commentFocused()){
			switch (key){
				case "n":
						handleNext();
					break;
				case "b":
						handlePrevious();
					break;
				case "z":
					modalData.setPass();
					break;
				case "x":
					modalData.setFail();
					break;
				case "c":
					modalData.setNone();
					break;
				case "Escape":
					handleClose();
					break;
				default:
					if (!isNaN(key)){
						modalData.setRating(parseInt(key));
					}
			}
		} else if (key == "Escape") {
			handleClose();
		}
	}

</script>
	<svelte:window on:keydown={handleKeydown}/>

	<div class="modal is-active"
	  transition:fade="{{ delay: 200, duration: 150 }}"
	  >
		<div class="modal-background" on:click={handleClose}></div>
		<div class="modal-card"
	   >
			<header class="modal-card-head">
				<p class="modal-card-title"> {item.name} </p>
				<button on:click={handleClose} class="delete"></button>
			</header>

			<section class="modal-card-body">
				<ItemRatingView 
					item={item}
					bind:this={modalData}
					bind:qc_rating={itemRating.failed}
					bind:comment={itemRating.comment}
					bind:rating_id={itemRating.rating}/>
			</section>

			<footer class="modal-card-foot">
				<button on:click={handlePrevious} class="button is-success">Previous</button>
				<button on:click={handleNext} class="button is-success">Next</button>
				<button on:click={handleClose} class="button is-warning">Exit</button>
			</footer>
		</div>
	</div>

<style>
	.modal-card{
		width: 80%
	}
</style>
