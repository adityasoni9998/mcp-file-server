#include<bits/stdc++.h>
using namespace std;
using ll = long long;
const ll INF = 1e6;

//ground truth: https://t5k.org/howmany.html

ll fn(ll x = INF){
    vector<bool> is_prime(x+1, 1);
    is_prime[0] = is_prime[1] = false;
    ll ans = 0;
    for(ll i=2;i<=x;i++){
        // cout << i << endl;
        if(!is_prime[i])continue;
        ans += 1;
        for(ll j=2;j*i<=x;j++){
            is_prime[j*i]=false;
        }
    }
    return ans;
}

int main(){
    cout << fn() << endl;
    return 0;
}