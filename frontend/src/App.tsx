
import { useEffect, useMemo, useState, type FormEvent } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts'
import './App.css'

const API_URL = (
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
).replace(/\/$/, '')

type PredictionProbabilities = {
  H: number
  D: number
  A: number
}

type PredictionResult = {
  home_team: string
  away_team: string
  prediction_date: string
  latest_historical_data_date: string
  logistic_regression: PredictionProbabilities
  random_forest: PredictionProbabilities
  disclaimer: string
}

type PredictionResponse = {
  status: string
  message: string
  prediction: PredictionResult
}

type TeamStanding = {
  Position: number
  Team: string
  Played: number
  Won: number
  Drawn: number
  Lost: number
  GF: number
  GA: number
  GD: number
  Points: number
}

type StandingsResponse = {
  status: string
  total_teams: number
  season: string
  data_through: string
  standings: TeamStanding[]
}

type PageName =
  | 'Overview'
  | 'Standings'
  | 'Team Analytics'
  | 'Match Predictions'

function App() {
  const [activePage, setActivePage] = useState<PageName>('Overview')

  const [teams, setTeams] = useState<string[]>([])
  const [standings, setStandings] = useState<TeamStanding[]>([])
  const [standingsDate, setStandingsDate] = useState('')

  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [predictionDate, setPredictionDate] = useState(
    new Date().toLocaleDateString('en-CA')
  )

  const [prediction, setPrediction] =
    useState<PredictionResult | null>(null)

  const [loadingTeams, setLoadingTeams] = useState(true)
  const [loadingStandings, setLoadingStandings] = useState(true)
  const [loadingPrediction, setLoadingPrediction] = useState(false)

  const [error, setError] = useState('')
  const [standingsError, setStandingsError] = useState('')

  const [searchTerm, setSearchTerm] = useState('')
  const [selectedTeam, setSelectedTeam] = useState('')

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [teamsResponse, standingsResponse] = await Promise.all([
          fetch(`${API_URL}/teams`),
          fetch(`${API_URL}/standings`)
        ])

        if (!teamsResponse.ok) {
          throw new Error('Could not load EPL teams.')
        }

        if (!standingsResponse.ok) {
          throw new Error('Could not load league standings.')
        }

        const teamsData = await teamsResponse.json()
        const standingsData: StandingsResponse =
          await standingsResponse.json()

        setTeams(teamsData.teams || [])
        setStandings(standingsData.standings || [])
        setStandingsDate(standingsData.data_through || '')

        if (teamsData.teams?.length > 0) {
          setHomeTeam(
            teamsData.teams.includes('Arsenal')
              ? 'Arsenal'
              : teamsData.teams[0]
          )

          setAwayTeam(
            teamsData.teams.includes('Chelsea')
              ? 'Chelsea'
              : teamsData.teams[1] || teamsData.teams[0]
          )
        }
      } catch (err) {
        setStandingsError(
          err instanceof Error ? err.message : 'Dashboard loading failed.'
        )
      } finally {
        setLoadingTeams(false)
        setLoadingStandings(false)
      }
    }

    loadDashboardData()
  }, [])

  const handlePrediction = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    setError('')
    setPrediction(null)

    if (homeTeam === awayTeam) {
      setError('Please select two different teams.')
      return
    }

    setLoadingPrediction(true)

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          home_team: homeTeam,
          away_team: awayTeam,
          prediction_date: predictionDate
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Prediction request failed.')
      }

      const result: PredictionResponse = data
      setPrediction(result.prediction)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Something went wrong.'
      )
    } finally {
      setLoadingPrediction(false)
    }
  }

  const formatProbability = (value: number) =>
    `${(value * 100).toFixed(1)}%`

  const formatDataDate = (date: string) => {
    if (!date) return 'Unavailable'

    const parsedDate = new Date(`${date}T00:00:00`)

    if (Number.isNaN(parsedDate.getTime())) return date

    return parsedDate.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    })
  }

  const filteredStandings = useMemo(() => {
    return standings.filter((team) =>
      team.Team.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }, [standings, searchTerm])

  const selectedTeamStats = standings.find(
    (team) => team.Team === selectedTeam
  )

  const topScoringTeams = useMemo(() => {
    return [...standings]
      .sort((a, b) => b.GF - a.GF)
      .slice(0, 10)
      .map((team) => ({
        team: team.Team,
        goalsScored: team.GF,
        goalsConceded: team.GA
      }))
  }, [standings])

  const topPointsTeams = useMemo(() => {
    return [...standings]
      .sort((a, b) => b.Points - a.Points || b.GD - a.GD)
      .slice(0, 10)
      .map((team) => ({
        team: team.Team,
        points: team.Points
      }))
  }, [standings])

  const selectedTeamResults = useMemo(() => {
    if (!selectedTeamStats) return []

    return [
      { result: 'Wins', matches: selectedTeamStats.Won },
      { result: 'Draws', matches: selectedTeamStats.Drawn },
      { result: 'Losses', matches: selectedTeamStats.Lost }
    ]
  }, [selectedTeamStats])

  const selectedTeamGoals = useMemo(() => {
    if (!selectedTeamStats) return []

    return [
      {
        type: 'Goals',
        scored: selectedTeamStats.GF,
        conceded: selectedTeamStats.GA
      }
    ]
  }, [selectedTeamStats])

  const navigation: { name: PageName; icon: string }[] = [
    { name: 'Overview', icon: '▦' },
    { name: 'Standings', icon: '🏆' },
    { name: 'Team Analytics', icon: '📊' },
    { name: 'Match Predictions', icon: '⚽' }
  ]

  const pageDescription: Record<PageName, string> = {
    Overview: 'Your EPL analytics command centre.',
    Standings: 'Explore the current league standings.',
    'Team Analytics': 'Explore team performance statistics.',
    'Match Predictions': 'Predict upcoming match outcomes using machine learning.'
  }

  const renderLeagueCharts = () => (
    <div className="charts-grid">
      <section className="panel chart-panel">
        <div className="panel-heading">
          <div>
            <span className="section-eyebrow">LEAGUE PERFORMANCE</span>
            <h2>Top Teams by Points</h2>
            <p>Ten teams with the highest points in the available standings.</p>
          </div>
          <span className="panel-icon">🏆</span>
        </div>

        <div className="chart-container">
          {loadingStandings ? (
            <p className="loading-message">Loading chart data...</p>
          ) : standingsError ? (
            <p className="error-message">{standingsError}</p>
          ) : topPointsTeams.length === 0 ? (
            <p className="empty-state">No standings data available.</p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={topPointsTeams}
                margin={{ top: 10, right: 15, left: 0, bottom: 35 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="team"
                  angle={-30}
                  textAnchor="end"
                  interval={0}
                  height={65}
                  tick={{ fontSize: 11 }}
                />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar
                  dataKey="points"
                  name="Points"
                  fill="#16a36a"
                  radius={[5, 5, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </section>

      <section className="panel chart-panel">
        <div className="panel-heading">
          <div>
            <span className="section-eyebrow">ATTACK AND DEFENCE</span>
            <h2>Goals Comparison</h2>
            <p>Goals scored and conceded by the ten highest-scoring teams.</p>
          </div>
          <span className="panel-icon">⚽</span>
        </div>

        <div className="chart-container">
          {loadingStandings ? (
            <p className="loading-message">Loading chart data...</p>
          ) : standingsError ? (
            <p className="error-message">{standingsError}</p>
          ) : topScoringTeams.length === 0 ? (
            <p className="empty-state">No goal data available.</p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={topScoringTeams}
                margin={{ top: 10, right: 15, left: 0, bottom: 35 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis
                  dataKey="team"
                  angle={-30}
                  textAnchor="end"
                  interval={0}
                  height={65}
                  tick={{ fontSize: 11 }}
                />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Bar
                  dataKey="goalsScored"
                  name="Goals Scored"
                  fill="#16a36a"
                  radius={[4, 4, 0, 0]}
                />
                <Bar
                  dataKey="goalsConceded"
                  name="Goals Conceded"
                  fill="#e58b42"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </section>
    </div>
  )

  const renderPredictionForm = () => (
    <section className="panel predictor-panel">
      <div className="panel-heading">
        <div>
          <span className="section-eyebrow">MACHINE LEARNING</span>
          <h2>Match Predictor</h2>
          <p>Choose two teams to generate a match prediction.</p>
        </div>
        <span className="panel-icon">⚽</span>
      </div>

      <form onSubmit={handlePrediction}>
        <div className="form-grid">
          <div className="form-group">
            <label htmlFor="homeTeam">Home Team</label>
            <select
              id="homeTeam"
              value={homeTeam}
              onChange={(event) => setHomeTeam(event.target.value)}
              disabled={loadingTeams}
              required
            >
              <option value="">Select home team</option>
              {teams.map((team) => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>

          <div className="versus">VS</div>

          <div className="form-group">
            <label htmlFor="awayTeam">Away Team</label>
            <select
              id="awayTeam"
              value={awayTeam}
              onChange={(event) => setAwayTeam(event.target.value)}
              disabled={loadingTeams}
              required
            >
              <option value="">Select away team</option>
              {teams.map((team) => (
                <option key={team} value={team}>{team}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group date-group">
          <label htmlFor="predictionDate">Match Date</label>
          <input
            id="predictionDate"
            type="date"
            value={predictionDate}
            onChange={(event) => setPredictionDate(event.target.value)}
            required
          />
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          className="primary-button"
          type="submit"
          disabled={loadingPrediction || loadingTeams}
        >
          {loadingPrediction ? 'Analysing Match...' : 'Generate Prediction'}
          <span>→</span>
        </button>
      </form>
    </section>
  )

  const renderPredictionResults = () => {
    if (!prediction) return null

    const models = [
      { name: 'Logistic Regression', data: prediction.logistic_regression },
      { name: 'Random Forest', data: prediction.random_forest }
    ]

    return (
      <section className="panel results-panel">
        <div className="panel-heading">
          <div>
            <span className="section-eyebrow">PREDICTION RESULTS</span>
            <h2>{prediction.home_team} vs {prediction.away_team}</h2>
            <p>Match date: {prediction.prediction_date}</p>
          </div>
          <span className="panel-icon">📈</span>
        </div>

        <div className="model-results">
          {models.map((model) => {
            const outcomes = [
              { label: 'Home Win', key: 'H' as const },
              { label: 'Draw', key: 'D' as const },
              { label: 'Away Win', key: 'A' as const }
            ]

            return (
              <div className="model-card" key={model.name}>
                <h3>{model.name}</h3>

                {outcomes.map((outcome) => (
                  <div className="probability-row" key={outcome.key}>
                    <div className="probability-label">
                      <span>{outcome.label}</span>
                      <strong>{formatProbability(model.data[outcome.key])}</strong>
                    </div>
                    <div className="progress-track">
                      <div
                        className="progress-fill"
                        style={{ width: `${model.data[outcome.key] * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )
          })}
        </div>

        <div className="prediction-disclaimer">
          <strong>Important:</strong> {prediction.disclaimer}
          <br />
          Historical data used: {prediction.latest_historical_data_date}
        </div>
      </section>
    )
  }

  const renderOverview = () => (
    <>
      <section className="welcome-banner">
        <div>
          <span className="section-eyebrow">GROUP 17 · SPORTS ANALYTICS</span>
          <h2>Welcome to EPL Analytics</h2>
          <p>
            Discover team performance, league standings and machine-learning
            match predictions.
          </p>
          <button
            className="banner-button"
            onClick={() => setActivePage('Match Predictions')}
          >
            Explore Match Predictions <span>→</span>
          </button>
        </div>
        <div className="banner-decoration">⚽</div>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">⚽</div>
          <span>Matches Analysed</span>
          <h3>460</h3>
          <small>Across two seasons</small>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <span>Current Season Teams</span>
          <h3>{standings.length || 20}</h3>
          <small>2026/2027 season</small>
        </div>

        <div className="stat-card">
          <div className="stat-icon">🤖</div>
          <span>ML Models</span>
          <h3>2</h3>
          <small>Logistic Regression & Random Forest</small>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📅</div>
          <span>Latest Match Data</span>
          <h3>{standingsDate ? formatDataDate(standingsDate) : 'Loading...'}</h3>
          <small>Latest available data</small>
        </div>
      </section>

      {renderLeagueCharts()}

      <div className="content-grid">
        {renderPredictionForm()}

        <section className="panel info-panel">
          <span className="section-eyebrow">ABOUT THE PROJECT</span>
          <h2>Data-driven football insights</h2>
          <p>
            This project uses historical English Premier League match data
            to analyse team performance and estimate match outcomes.
          </p>

          <div className="feature-list">
            <div><span>✓</span> Team performance analysis</div>
            <div><span>✓</span> League standings</div>
            <div><span>✓</span> Historical match statistics</div>
            <div><span>✓</span> Machine learning predictions</div>
          </div>

          <button
            className="text-button"
            onClick={() => setActivePage('Standings')}
          >
            View League Table →
          </button>
        </section>
      </div>

      {renderPredictionResults()}
    </>
  )

  const renderStandings = () => (
    <section className="panel standings-panel">
      <div className="panel-heading standings-heading">
        <div>
          <span className="section-eyebrow">2026/2027 SEASON</span>
          <h2>Premier League Table</h2>
          <p>
            Partial standings based on available completed matches.
            Data through {standingsDate || 'the latest available date'}.
          </p>
        </div>
        <span className="panel-icon">🏆</span>
      </div>

      <div className="table-toolbar">
        <input
          type="search"
          placeholder="Search for a team..."
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          aria-label="Search teams"
        />
        <span>{filteredStandings.length} teams</span>
      </div>

      {loadingStandings ? (
        <p className="loading-message">Loading league standings...</p>
      ) : standingsError ? (
        <p className="error-message">{standingsError}</p>
      ) : (
        <div className="table-wrapper">
          <table className="standings-table">
            <thead>
              <tr>
                <th>Pos</th><th>Club</th><th>P</th><th>W</th><th>D</th>
                <th>L</th><th>GF</th><th>GA</th><th>GD</th><th>Pts</th>
              </tr>
            </thead>
            <tbody>
              {filteredStandings.map((team) => (
                <tr
                  key={team.Team}
                  className={team.Position <= 4 ? 'top-four-row' : ''}
                  onClick={() => {
                    setSelectedTeam(team.Team)
                    setActivePage('Team Analytics')
                  }}
                >
                  <td>{team.Position}</td>
                  <td className="club-name">{team.Team}</td>
                  <td>{team.Played}</td>
                  <td>{team.Won}</td>
                  <td>{team.Drawn}</td>
                  <td>{team.Lost}</td>
                  <td>{team.GF}</td>
                  <td>{team.GA}</td>
                  <td className={team.GD > 0 ? 'positive' : team.GD < 0 ? 'negative' : ''}>
                    {team.GD > 0 ? `+${team.GD}` : team.GD}
                  </td>
                  <td className="points-cell">{team.Points}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="table-note">
        Click any team row to view its performance statistics.
        <br />
        P: Played · W: Won · D: Drawn · L: Lost · GF: Goals For · GA: Goals Against · GD: Goal Difference · Pts: Points.
      </div>
    </section>
  )

  const renderTeamAnalytics = () => (
    <section className="panel analytics-panel">
      <div className="panel-heading">
        <div>
          <span className="section-eyebrow">TEAM PERFORMANCE</span>
          <h2>Team Analytics</h2>
          <p>Select a club to explore its current-season statistics.</p>
        </div>
        <span className="panel-icon">📊</span>
      </div>

      <div className="form-group team-selector">
        <label htmlFor="analyticsTeam">Select Team</label>
        <select
          id="analyticsTeam"
          value={selectedTeam}
          onChange={(event) => setSelectedTeam(event.target.value)}
        >
          <option value="">Choose a team</option>
          {standings.map((team) => (
            <option key={team.Team} value={team.Team}>{team.Team}</option>
          ))}
        </select>
      </div>

      {selectedTeamStats ? (
        <>
          <div className="team-profile">
            <div>
              <span className="section-eyebrow">LEAGUE POSITION</span>
              <h2>{selectedTeamStats.Team}</h2>
              <p>Position #{selectedTeamStats.Position}</p>
            </div>
            <div className="team-points">
              <strong>{selectedTeamStats.Points}</strong>
              <span>Points</span>
            </div>
          </div>

          <div className="stats-grid team-stats-grid">
            <div className="stat-card"><span>Matches Played</span><h3>{selectedTeamStats.Played}</h3></div>
            <div className="stat-card"><span>Wins</span><h3>{selectedTeamStats.Won}</h3></div>
            <div className="stat-card"><span>Draws</span><h3>{selectedTeamStats.Drawn}</h3></div>
            <div className="stat-card"><span>Losses</span><h3>{selectedTeamStats.Lost}</h3></div>
            <div className="stat-card"><span>Goals Scored</span><h3>{selectedTeamStats.GF}</h3></div>
            <div className="stat-card"><span>Goals Conceded</span><h3>{selectedTeamStats.GA}</h3></div>
            <div className="stat-card">
              <span>Goal Difference</span>
              <h3>{selectedTeamStats.GD > 0 ? `+${selectedTeamStats.GD}` : selectedTeamStats.GD}</h3>
            </div>
            <div className="stat-card">
              <span>Points per Match</span>
              <h3>{(selectedTeamStats.Points / Math.max(selectedTeamStats.Played, 1)).toFixed(2)}</h3>
            </div>
          </div>

          <div className="charts-grid team-charts-grid">
            <section className="panel chart-panel">
              <div className="panel-heading">
                <div>
                  <span className="section-eyebrow">RESULT BREAKDOWN</span>
                  <h2>Match Results</h2>
                  <p>Wins, draws and losses.</p>
                </div>
              </div>

              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={selectedTeamResults}
                    margin={{ top: 15, right: 20, left: 0, bottom: 10 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="result" />
                    <YAxis allowDecimals={false} domain={[0, 'auto']} />
                    <Tooltip />
                    <Bar
                      dataKey="matches"
                      name="Matches"
                      fill="#16a36a"
                      radius={[5, 5, 0, 0]}
                      maxBarSize={65}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>

            <section className="panel chart-panel">
              <div className="panel-heading">
                <div>
                  <span className="section-eyebrow">GOAL ANALYSIS</span>
                  <h2>Goals Scored vs Conceded</h2>
                  <p>Attacking and defensive output.</p>
                </div>
              </div>

              <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={selectedTeamGoals}
                    margin={{ top: 15, right: 20, left: 0, bottom: 10 }}
                    barCategoryGap="35%"
                  >
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="type" />
                    <YAxis allowDecimals={false} domain={[0, 'auto']} />
                    <Tooltip />
                    <Legend />
                    <Bar
                      dataKey="scored"
                      name="Goals Scored"
                      fill="#16a36a"
                      radius={[5, 5, 0, 0]}
                      maxBarSize={65}
                    />
                    <Bar
                      dataKey="conceded"
                      name="Goals Conceded"
                      fill="#e58b42"
                      radius={[5, 5, 0, 0]}
                      maxBarSize={65}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          </div>
        </>
      ) : (
        <div className="empty-state">
          <span>📊</span>
          <h3>Select a team to begin</h3>
          <p>
            Team statistics and charts will appear here using the available
            2026/2027 season results.
          </p>
        </div>
      )}
    </section>
  )

  const renderMatchPredictions = () => (
    <>
      {renderPredictionForm()}
      {renderPredictionResults()}
    </>
  )

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">⚽</div>
          <div>
            <h1>EPL<span>Analytics</span></h1>
            <small>GROUP 17 PROJECT</small>
          </div>
        </div>

        <div className="sidebar-section-label">MENU</div>

        <nav className="sidebar-nav">
          {navigation.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${activePage === item.name ? 'active' : ''}`}
              onClick={() => setActivePage(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.name}
              {activePage === item.name && <span className="active-indicator" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <span className="status-dot" />
            API Connected
          </div>
          <small>Powered by Python & React</small>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="breadcrumb">EPL ANALYTICS /</span>
            <h1>{activePage}</h1>
            <p>{pageDescription[activePage]}</p>
          </div>

          <div className="topbar-right">
            <span className="season-badge">2026/2027 SEASON</span>
            <div className="user-avatar">G17</div>
          </div>
        </header>

        <div className="page-content">
          {activePage === 'Overview' && renderOverview()}
          {activePage === 'Standings' && renderStandings()}
          {activePage === 'Team Analytics' && renderTeamAnalytics()}
          {activePage === 'Match Predictions' && renderMatchPredictions()}
        </div>

        <footer className="app-footer">
          <p>
            EPL Sports Analytics · Group 17 · Built with Python, FastAPI
            and React.
          </p>
          <span>Predictions are estimates, not guarantees.</span>
        </footer>
      </main>
    </div>
  )
}

export default App
