window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};


const deleteBtn = document.getElementById('delete-button')
deleteBtn.onclick = function(e) {
  const venueId = e.target.dataset['id']
  fetch('/venues/' + venueId, {
    method: 'DELETE'
  })

}

window.onload = function(){
    const deleteBtn = document.getElementById('delete-button')
    deleteBtn.onclick = function(e) {
      const venueId = e.target.dataset['id']
      fetch('/venues/' + venueId, {
          method: 'DELETE'
        }).then(function() {
          window.location.href = "/venues";
        })
    }

    const editBtn = document.getElementById('edit-button')
    editBtn.onclick = function(e) {
      const venueId = e.target.dataset['id']
      window.location = '/venues/' + venueId + '/edit'
    }
}
