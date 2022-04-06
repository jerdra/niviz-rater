export function getNext(id, previous, arr, skipRated){
  const i = arr.map(e => e.id).indexOf(id);
  let searchArr = [
    ...arr.slice(i + 1, arr.length),
    ...arr.slice(0, i)
  ]
  if (previous) {
    searchArr = searchArr.reverse();
  }

  // Now filter for any remaining
  const next = searchArr.filter(e => (!skipRated || e.failed == null));
  return next

}
