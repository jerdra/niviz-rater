<!--
	@component

	Display of Modal core contents including:
	- Images
	- Current rating
	- Comment box that can be updated
	- Dropdown containing available ratings
-->


<script>

	import { onMount } from 'svelte';

	export let item;
	export let qc_rating;
	export let comment;
	export let rating_id;
	let focused = false;
  $: console.log(item);

	let passfailArr;
	$: passfailArr = [
		{value: false, name: "Pass", checked: qc_rating==false || null},
		{value: true, name: "Fail", checked: qc_rating==true || null},
		{value: null, name: "None", checked: qc_rating==null || null}
	];

	function markRadioDefault(node, checked){
		node.checked=checked;
	}

	let availableRatings = item.availableRatings.map(r => r.id);
	export function setRating(num){
		if (availableRatings.includes(num)){
			rating_id=num;
		} else {
			console.log("Not an available rating")
		}
	}

	export function commentFocused(){
		return focused;
	}


	export const setPass = () => {qc_rating = false}
	export const setFail = () => {qc_rating = true}
	export const setNone = () => {qc_rating = null}
	const onFocus = () => focused=true;
	const onBlur = () => focused=false;

	$: console.log(focused);
</script>

{#if item}
	{#each item.images as image (image)}
		<div class="block">
			<object width="100%" data={image} type="image/svg+xml">
				<img src={image}/>
			</object>
		</div>
	{/each}
	<div class="tile is-parent">
		<div class="tile is-parent is-vertical">
			<div class="tile is-child">
				<div class="select">
					<select bind:value={rating_id}>
						<option value="" selected disabled hidden>Select rating</option>
						{#each item.availableRatings as rating (rating)}
							<option value={rating.id}>{rating.name}</option>
						{/each}
					</select>
				</div>
			</div>
			<div class="tile is-child">
				<div class="control">
					{#each passfailArr as {name, value, checked} (name)}
						<label class="radio">
							<input type="radio"
								  use:markRadioDefault={checked}
								  name="passfail" 
								 {value} bind:group={qc_rating}>
							{name}
						</label>
					{/each}
				</div>
			</div>
		</div>
		<div class="tile is-child">
			Comments:
			<textarea bind:value={comment} on:focus={onFocus} on:blur={onBlur}
				class="textarea" placeholder="Comments"></textarea>
		</div>
	</div>
{/if}

<style>
</style>

