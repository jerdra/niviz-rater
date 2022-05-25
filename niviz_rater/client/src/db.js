/*
 * Utilities to interact with the back-end DB serving entities
 */


async function postDB(endpoint, content){
	// Generic post function for pushing JSON data to the DB
	const response = await fetch(
		endpoint,
		{
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(content)
		}
	)
	return response.status;
}

export async function fetchEntities(){
	const response = await fetch('./api/spreadsheet')
	let entities = await response.json();

	// Return sorted entities
	return entities.entities.sort((a,b) => {
		return (
			a.rowName.localeCompare(b.rowName)
			|| a.columnName.localeCompare(b.columnName)
		)
	});
}

export const updateRating = async function(rating){

	const statusCode = await postDB('./api/entity', rating);
	if (statusCode != 200){
		alert("Failed to POST to DB!");
	}
	const entities = await fetchEntities();
	return entities
}

export const getOverview = async function(){
	const response = await fetch("./api/overview");
	return await response.json();
}

export async function exportCsv(){
	const response = await fetch('./api/export');
	return await response.text()
};

export async function getEntityView(id){
	/* Fetch view for entity */
	let response = await fetch(`./api/entity/${id}/view`)
	let entity_view = await response.json();
  return {
    rating: entity_view.entityRating,
    ratingName: function() { return this.rating.name },
    isRated: function() { return this.rating.name != "None" },
    comment: entity_view.entityComment,
    id: entity_view.entityId,
    annotation: entity_view.entityAnnotation,
    availableAnnotations: entity_view.entityAvailableAnnotations,
    images: entity_view.entityImages,
    name: entity_view.entityName
  }
}
