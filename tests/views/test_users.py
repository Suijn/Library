"""A testing module for the views/users.py module."""

import json
from bookstore.users.models import User

class TestUsers:

    def test_getUserReservations(self, client, normal_access_token, db_populate_reservations):
        """
        Test the getUserReservations function.

        :assert: status code is 200.
        :assert: api returns a proper response.
        :assert: user gets only his own reservations. 
        """
        user = User.query.filter(User.email == 'user@test.com').one()

        response = client.get(
            '/users/getReservations',
            headers = {
                'Authorization': 'Bearer ' + normal_access_token
            }
        )

        assert response.status_code == 200
        assert response.json
        
        response_keys = [x for x in response.json[0].keys()]

        assert set(['book_id','reserved_by','expected_end_date','start_date','status','was_prolonged']).issubset(set(response_keys))
        assert response.json[0]['reserved_by'] == user.id
    
