import axios from 'axios';
const API_URL = 'http://localhost:8000';

export default class JobsService{

    constructor(){}

    getPositions() {
        const url = `${API_URL}/api/positions/`;
        return axios.get(url).then(response => response.data);
    }
}